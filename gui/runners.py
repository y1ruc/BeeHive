"""
BeeHive GUI — Tool execution layer.

Runs BeeHive tools inside the GUI by:
  - redirecting stdout/stderr to the console widget
  - replacing swarm_core.ask / swarm_core.pause with GUI dialogs
  - running everything in a worker thread so the UI stays responsive
"""

import importlib
import io
import os
import re
import sys
import threading
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Callable, Dict, List, Optional


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

from PySide6.QtCore import QObject, QThread, Signal, Slot


# ---------------------------------------------------------------------------
# Stdout bridge
# ---------------------------------------------------------------------------

class GuiStream(io.TextIOBase):
    """A write-only text stream that forwards lines to a callback."""

    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback
        self._buffer = ""

    def writable(self):
        return True

    def write(self, text: str) -> int:
        if text:
            self._buffer += text
            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                self.callback(_ANSI_RE.sub("", line + "\n"))
        return len(text)

    def flush(self):
        if self._buffer:
            self.callback(self._buffer)
            self._buffer = ""


# ---------------------------------------------------------------------------
# Ask / pause hooks (installed per-run so the GUI can show dialogs)
# ---------------------------------------------------------------------------

class InputHooks:
    def __init__(self, ask_callback: Callable[[str, str], str], pause_callback: Callable[[], None]):
        self.ask_callback = ask_callback
        self.pause_callback = pause_callback
        self._orig = {}

    def _gui_ask(self, label: str, default: str = "") -> str:
        return self.ask_callback(label, default)

    def _gui_pause(self):
        self.pause_callback()

    def install(self):
        import swarm_core
        self._orig["ask"] = swarm_core.ask
        self._orig["pause"] = swarm_core.pause
        swarm_core.ask = self._gui_ask
        swarm_core.pause = self._gui_pause

        # Patch already-imported modules that shadow these names.
        for mod_name, mod in list(sys.modules.items()):
            if mod is None or not hasattr(mod, "__dict__"):
                continue
            d = mod.__dict__
            if "ask" in d and d["ask"] is self._orig["ask"]:
                d["ask"] = self._gui_ask
            if "pause" in d and d["pause"] is self._orig["pause"]:
                d["pause"] = self._gui_pause

    def uninstall(self):
        import swarm_core
        if "ask" in self._orig:
            swarm_core.ask = self._orig["ask"]
        if "pause" in self._orig:
            swarm_core.pause = self._orig["pause"]
        for mod_name, mod in list(sys.modules.items()):
            if mod is None or not hasattr(mod, "__dict__"):
                continue
            d = mod.__dict__
            if "ask" in d and d["ask"] in (self._gui_ask, self._orig.get("ask")):
                d["ask"] = self._orig["ask"]
            if "pause" in d and d["pause"] in (self._gui_pause, self._orig.get("pause")):
                d["pause"] = self._orig["pause"]


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Discovers tools from the existing beehive.py structure without
    launching the CLI menu."""

    def __init__(self, root: str):
        self.root = root
        self.categories: List[dict] = []
        self.tools: Dict[str, List[dict]] = {}
        self._load()

    def _load(self):
        # Add category dirs to path just like beehive.py does.
        if self.root not in sys.path:
            sys.path.insert(0, self.root)
        for cat in ("web", "network", "crypto", "pass", "discord", "files", "misc"):
            catdir = os.path.join(self.root, cat)
            if os.path.isdir(catdir):
                for sub in sorted(os.listdir(catdir)):
                    subdir = os.path.join(catdir, sub)
                    if os.path.isdir(subdir) and subdir not in sys.path:
                        sys.path.insert(0, subdir)

        # Import beehive.py for the metadata tables, but patch menu so it never runs.
        import beehive
        self.categories = [
            {
                "id": cid,
                "name": name,
                "color": color,
                "icon": icon,
                "desc": desc,
            }
            for cid, name, color, icon, desc in beehive.CATEGORIES
        ]
        for cat_id, items in beehive.TOOLS.items():
            self.tools[cat_id] = [
                {
                    "name": name,
                    "desc": desc,
                    "handler": fn,
                    "module": getattr(fn, "__module__", None),
                }
                for name, desc, fn in items
            ]


# ---------------------------------------------------------------------------
# Worker thread
# ---------------------------------------------------------------------------

class ToolWorker(QObject):
    output = Signal(str)
    finished = Signal(bool, str)
    request_input = Signal(str, str)
    request_pause = Signal()
    input_ready = Signal(str)
    pause_ready = Signal()

    def __init__(self, handler: Callable, args=(), kwargs=None):
        super().__init__()
        self.handler = handler
        self.args = args
        self.kwargs = kwargs or {}
        self._input_value: Optional[str] = None
        self._pause_done = threading.Event()
        self._input_event = threading.Event()
        self._cancelled = False

    def run(self):
        try:
            hooks = InputHooks(
                ask_callback=self._gui_ask,
                pause_callback=self._gui_pause,
            )
            hooks.install()

            def emit_line(line: str):
                if not self._cancelled:
                    self.output.emit(line)

            stream = GuiStream(emit_line)
            with redirect_stdout(stream), redirect_stderr(stream):
                result = self.handler(*self.args, **self.kwargs)
                # Some tools are async.
                if result is not None and hasattr(result, "__await__"):
                    import asyncio
                    asyncio.run(result)
            stream.flush()
            self.finished.emit(True, "")
        except Exception as e:
            stream = io.StringIO()
            traceback.print_exc(file=stream)
            self.output.emit(stream.getvalue())
            self.finished.emit(False, str(e))
        finally:
            hooks.uninstall()

    def _gui_ask(self, label: str, default: str = "") -> str:
        self._input_event.clear()
        self._input_value = None
        self.request_input.emit(label, default)
        self._input_event.wait()
        return self._input_value or ""

    @Slot(str)
    def provide_input(self, value: str):
        self._input_value = value
        self._input_event.set()

    def _gui_pause(self):
        self._pause_done.clear()
        self.request_pause.emit()
        self._pause_done.wait()

    @Slot()
    def acknowledge_pause(self):
        self._pause_done.set()

    def cancel(self):
        self._cancelled = True
        self.provide_input("")
        self.acknowledge_pause()


# ---------------------------------------------------------------------------
# Runner manager
# ---------------------------------------------------------------------------

class ToolRunner(QObject):
    output = Signal(str)
    finished = Signal(bool, str)
    request_input = Signal(str, str)
    request_pause = Signal()
    started = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: Optional[QThread] = None
        self._worker: Optional[ToolWorker] = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def run(self, handler: Callable, args=(), kwargs=None):
        if self.is_running():
            return
        self.started.emit()
        self._thread = QThread()
        self._worker = ToolWorker(handler, args, kwargs or {})
        self._worker.moveToThread(self._thread)

        self._worker.output.connect(self.output.emit)
        self._worker.finished.connect(self._on_finished)
        self._worker.request_input.connect(self.request_input.emit)
        self._worker.request_pause.connect(self.request_pause.emit)
        self._thread.started.connect(self._worker.run)

        self._thread.start()

    def provide_input(self, value: str):
        if self._worker:
            self._worker.provide_input(value)

    def acknowledge_pause(self):
        if self._worker:
            self._worker.acknowledge_pause()

    def cancel(self):
        if self._worker:
            self._worker.cancel()

    def _on_finished(self, ok: bool, msg: str):
        self.finished.emit(ok, msg)
        if self._thread:
            self._thread.quit()
            self._thread.wait(2000)
        self._thread = None
        self._worker = None
