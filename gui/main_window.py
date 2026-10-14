"""
BeeHive GUI — Main application window (Maximalist edition).
"""

import os
import random
from functools import partial

from PySide6.QtCore import QEvent, QPoint, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDoubleSpinBox, QFileDialog,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSpinBox, QSplitter,
    QVBoxLayout, QWidget,
)

from .components import (
    CategoryButton, ConsoleWidget, Floater, PatternBackground, SearchBox,
    ShadowFrame, ShadowLabel, TitleBar, ToolCard,
)
from .forms import FloodDialog
from .runners import ToolRegistry, ToolRunner
from .theme import (
    HiveColor, THEMES, accent, apply_theme, clash, font_body, font_display,
    font_heading, font_mono,
)


# ---------------------------------------------------------------------------
# Input dialog
# ---------------------------------------------------------------------------

class AskDialog(QDialog):
    def __init__(self, label: str, default: str, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(380)

        self.answer = default

        container = ShadowFrame(self, border_color=HiveColor.MAGENTA, bg_color=HiveColor.MUTED,
                                shadow_layers=[(HiveColor.YELLOW, 8), (HiveColor.CYAN, 16)],
                                radius=24, border_width=4)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(22, 20, 22, 20)
        inner.setSpacing(14)

        lbl = ShadowLabel(label, shadows=[
            (QPoint(1, 1), HiveColor.PURPLE),
            (QPoint(2, 2), HiveColor.MAGENTA),
        ])
        lbl.setFont(font_heading(11, QFont.Black))
        lbl.setTextColor(HiveColor.FG)
        lbl.setWordWrap(True)
        inner.addWidget(lbl)

        self.edit = QLineEdit(default)
        self.edit.setFixedHeight(44)
        self.edit.returnPressed.connect(self.accept)
        inner.addWidget(self.edit)

        btns = QHBoxLayout()
        btns.addStretch()
        ok = QPushButton("OK")
        ok.setObjectName("primary")
        ok.setFixedWidth(90)
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        inner.addLayout(btns)

    def accept(self):
        self.answer = self.edit.text()
        super().accept()


# ---------------------------------------------------------------------------
# Pause dialog
# ---------------------------------------------------------------------------

class PauseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(300)

        container = ShadowFrame(self, border_color=HiveColor.CYAN, bg_color=HiveColor.MUTED,
                                shadow_layers=[(HiveColor.MAGENTA, 8), (HiveColor.YELLOW, 16)],
                                radius=24, border_width=4)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(22, 20, 22, 20)
        inner.setSpacing(14)

        lbl = ShadowLabel("Tool paused — press Continue to proceed.", shadows=[
            (QPoint(1, 1), HiveColor.PURPLE),
        ])
        lbl.setFont(font_heading(11, QFont.Black))
        lbl.setTextColor(HiveColor.FG)
        lbl.setAlignment(Qt.AlignCenter)
        inner.addWidget(lbl)

        ok = QPushButton("Continue")
        ok.setObjectName("primary")
        ok.setFixedHeight(44)
        ok.clicked.connect(self.accept)
        inner.addWidget(ok)


# ---------------------------------------------------------------------------
# Settings panel
# ---------------------------------------------------------------------------

class SettingsPanel(QWidget):
    theme_changed = Signal(str)
    settings_saved = Signal()

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = dict(settings)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(18)

        header = ShadowLabel("Hive Settings", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
            (QPoint(6, 6), HiveColor.CYAN),
        ])
        header.setFont(font_display(22, QFont.Black))
        header.setTextColor(HiveColor.YELLOW)
        layout.addWidget(header)

        sub = QLabel("Configure global defaults used by swarm tools.")
        sub.setFont(font_body(10))
        sub.setStyleSheet(f"color: {HiveColor.TEXT_SECONDARY.name()};")
        layout.addWidget(sub)

        # Theme
        self.theme_box = QComboBox()
        self.theme_box.addItems(list(THEMES.keys()))
        self.theme_box.setCurrentText(self.settings.get("theme", "honey"))
        self.theme_box.currentTextChanged.connect(self._on_theme_changed)
        self._row(layout, "Theme", self.theme_box)

        # Concurrency
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 64)
        self.concurrency_spin.setValue(self.settings.get("concurrency", 8))
        self._row(layout, "Concurrency", self.concurrency_spin)

        # Delay
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 10.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setValue(self.settings.get("delay", 0.0))
        self._row(layout, "Join Delay", self.delay_spin)

        # Name mode
        self.name_mode = QComboBox()
        self.name_mode.addItems(["prefix", "random", "file"])
        self.name_mode.setCurrentText(self.settings.get("name_mode", "prefix"))
        self.name_mode.currentTextChanged.connect(self._on_name_mode_changed)
        self._row(layout, "Name Mode", self.name_mode)

        # Prefix
        self.prefix_edit = QLineEdit(self.settings.get("name_prefix", "Bee"))
        self._row(layout, "Prefix", self.prefix_edit)

        # Name file
        file_row = QHBoxLayout()
        self.file_edit = QLineEdit(self.settings.get("name_file", ""))
        self.file_edit.setPlaceholderText("names.txt")
        self.file_btn = QPushButton("Browse")
        self.file_btn.setFixedWidth(80)
        self.file_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self.file_edit, 1)
        file_row.addWidget(self.file_btn)
        self._row(layout, "Name File", file_row)

        self._on_name_mode_changed(self.name_mode.currentText())

        layout.addStretch()

        save = QPushButton("Save Settings")
        save.setObjectName("primary")
        save.setFixedHeight(48)
        save.clicked.connect(self._save)
        layout.addWidget(save)

    def _row(self, layout, label: str, widget):
        row = QHBoxLayout()
        lbl = ShadowLabel(label, shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        lbl.setFont(font_heading(10, QFont.Black))
        lbl.setTextColor(HiveColor.TEXT_SECONDARY)
        lbl.setFixedWidth(110)
        row.addWidget(lbl)
        if isinstance(widget, QHBoxLayout):
            row.addLayout(widget, 1)
        else:
            row.addWidget(widget, 1)
        layout.addLayout(row)

    def _on_theme_changed(self, name: str):
        self.theme_changed.emit(name)

    def _on_name_mode_changed(self, mode: str):
        self.prefix_edit.setEnabled(mode == "prefix")
        self.file_edit.setEnabled(mode == "file")
        self.file_btn.setEnabled(mode == "file")

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Name File", "", "Text Files (*.txt)")
        if path:
            self.file_edit.setText(path)

    def _save(self):
        self.settings.update({
            "theme": self.theme_box.currentText(),
            "concurrency": self.concurrency_spin.value(),
            "delay": self.delay_spin.value(),
            "name_mode": self.name_mode.currentText(),
            "name_prefix": self.prefix_edit.text(),
            "name_file": self.file_edit.text(),
        })
        try:
            import json
            with open(os.path.join(os.path.dirname(__file__), "..", "beehive.json"), "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))
            return
        self.settings_saved.emit()


# ---------------------------------------------------------------------------
# Tool detail / runner panel
# ---------------------------------------------------------------------------

class ToolPanel(QWidget):
    run_tool = Signal(object, tuple, dict)
    run_tool_stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tool = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.icon_lbl = ShadowLabel("◈", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
        ])
        self.icon_lbl.setFont(font_display(32, QFont.Black))
        self.icon_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.icon_lbl)

        self.name_lbl = ShadowLabel("Select a tool", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
            (QPoint(6, 6), HiveColor.CYAN),
        ])
        self.name_lbl.setFont(font_display(18, QFont.Black))
        layout.addWidget(self.name_lbl)

        self.desc_lbl = QLabel("Click a tool card from the grid to get started.")
        self.desc_lbl.setFont(font_body(10))
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {HiveColor.TEXT_SECONDARY.name()};")
        layout.addWidget(self.desc_lbl)

        self.module_lbl = QLabel("")
        self.module_lbl.setFont(font_mono(9))
        self.module_lbl.setStyleSheet(f"color: {HiveColor.TEXT_DISABLED.name()};")
        layout.addWidget(self.module_lbl)

        self.status_lbl = ShadowLabel("", shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        self.status_lbl.setFont(font_heading(9, QFont.Black))
        self.status_lbl.setTextColor(HiveColor.TEXT_DISABLED)
        self.status_lbl.setWordWrap(True)
        layout.addWidget(self.status_lbl)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run Tool")
        self.run_btn.setObjectName("primary")
        self.run_btn.setFixedHeight(52)
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._on_run)
        btn_row.addWidget(self.run_btn, 1)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setFixedHeight(52)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def set_tool(self, tool: dict, accent_color: str):
        self.current_tool = tool
        self.icon_lbl.setTextColor(HiveColor.HONEY)
        self.name_lbl.setText(tool["name"])
        self.desc_lbl.setText(tool["desc"])
        self.module_lbl.setText(f"module: {tool.get('module', 'unknown')}")
        self.run_btn.setEnabled(True)
        self.run_btn.setText(f"Run {tool['name']}")
        self.stop_btn.setEnabled(False)
        self.status_lbl.setText("Ready")
        self.status_lbl.setTextColor(HiveColor.TEXT_DISABLED)

    def set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        if running:
            self.status_lbl.setText("Running...")
            self.status_lbl.setTextColor(HiveColor.YELLOW)
        else:
            self.status_lbl.setText("Ready")
            self.status_lbl.setTextColor(HiveColor.TEXT_DISABLED)

    def _on_run(self):
        if self.current_tool:
            self.run_tool.emit(self.current_tool["handler"], (), {})

    def _on_stop(self):
        self.run_tool_stop_requested.emit()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.registry = ToolRegistry(os.path.dirname(os.path.dirname(__file__)))
        self.runner = ToolRunner(self)
        self.runner.output.connect(self._on_output)
        self.runner.finished.connect(self._on_finished)
        self.runner.request_input.connect(self._on_request_input)
        self.runner.request_pause.connect(self._on_request_pause)
        self.runner.started.connect(self._on_started)

        self._settings = self._load_settings()
        self._current_category = self.registry.categories[0]["id"] if self.registry.categories else None
        self._category_buttons: list = []
        self._floaters: list = []

        self._build_ui()
        self._apply_window_shape()
        self._set_theme(self._settings.get("theme", "honey"))

    def _load_settings(self):
        import json
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beehive.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "concurrency": 8,
                "delay": 0.0,
                "name_mode": "prefix",
                "name_prefix": "Bee",
                "name_file": "",
                "theme": "honey",
            }

    def _build_ui(self):
        central = ShadowFrame(self, border_color=HiveColor.MAGENTA, bg_color=HiveColor.BG,
                              shadow_layers=[(HiveColor.YELLOW, 10), (HiveColor.CYAN, 20)],
                              radius=12, border_width=4)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self, "BeeHive")
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # Body: sidebar | main splitter
        body = QHBoxLayout()
        body.setContentsMargins(14, 14, 14, 14)
        body.setSpacing(14)
        main_layout.addLayout(body)

        # Sidebar
        sidebar = ShadowFrame(self, border_color=HiveColor.CYAN, bg_color=HiveColor.MUTED,
                              shadow_layers=[(HiveColor.MAGENTA, 8), (HiveColor.YELLOW, 16)],
                              radius=24, border_width=4)
        sidebar.setFixedWidth(240)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(14, 18, 14, 18)
        sb.setSpacing(10)

        # Pattern overlay
        sb_pattern = PatternBackground(sidebar, pattern="dots", color=HiveColor.CYAN, density=24)
        sb_pattern.setGeometry(sidebar.rect())
        sb_pattern.lower()
        self._sb_pattern = sb_pattern

        logo = ShadowLabel("◈  BEEHIVE", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
            (QPoint(6, 6), HiveColor.CYAN),
        ])
        logo.setFont(font_display(16, QFont.Black))
        logo.setTextColor(HiveColor.YELLOW)
        sb.addWidget(logo)

        ver = ShadowLabel("multi-tool launcher", shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        ver.setFont(font_body(8, QFont.Bold))
        ver.setTextColor(HiveColor.TEXT_DISABLED)
        sb.addWidget(ver)

        sb.addSpacing(20)

        for i, cat in enumerate(self.registry.categories):
            btn = CategoryButton(cat["icon"], cat["name"], cat["color"], index=i)
            btn.clicked.connect(partial(self._select_category, cat["id"]))
            self._category_buttons.append(btn)
            sb.addWidget(btn)

        sb.addStretch()

        self.settings_btn = CategoryButton("◆", "Settings", HiveColor.TEXT_SECONDARY.name(), index=100)
        self.settings_btn.clicked.connect(self._show_settings)
        sb.addWidget(self.settings_btn)

        self.about_btn = CategoryButton("✦", "About", HiveColor.TEXT_SECONDARY.name(), index=101)
        self.about_btn.clicked.connect(self._show_about)
        sb.addWidget(self.about_btn)

        body.addWidget(sidebar)

        # Main horizontal splitter
        self.h_splitter = QSplitter(Qt.Horizontal)
        self.h_splitter.setHandleWidth(4)
        body.addWidget(self.h_splitter, 1)

        # Center stack: vertical splitter with grid + console
        center_stack = QWidget()
        center_layout = QVBoxLayout(center_stack)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.v_splitter = QSplitter(Qt.Vertical)
        self.v_splitter.setHandleWidth(4)
        center_layout.addWidget(self.v_splitter)

        # Center: tools grid
        center = ShadowFrame(self, border_color=HiveColor.YELLOW, bg_color=HiveColor.MUTED,
                             shadow_layers=[(HiveColor.MAGENTA, 10), (HiveColor.CYAN, 20)],
                             radius=24, border_width=4)
        cl = QVBoxLayout(center)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(16)

        # A quiet honeycomb gives the work surface texture without returning
        # to the previous high-contrast neon pattern stack.
        self.pt_comb = PatternBackground(center, pattern="comb", color=HiveColor.HONEY, density=28)
        self.pt_comb.lower()

        # Big background typography
        self.bg_text = ShadowLabel("HIVE", shadows=[(QPoint(3, 3), HiveColor.BARK)])
        self.bg_text.setFont(font_display(112, QFont.Black))
        watermark = QColor(HiveColor.HONEY)
        watermark.setAlpha(25)
        self.bg_text.setTextColor(watermark)
        self.bg_text.setAlignment(Qt.AlignCenter)
        self.bg_text.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.bg_text.lower()

        top = QHBoxLayout()
        self.search = SearchBox()
        self.search.textChanged.connect(self._filter_tools)
        top.addWidget(self.search)
        cl.addLayout(top)

        self.category_title = ShadowLabel("Web Bots & Nukers", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
        ])
        self.category_title.setFont(font_display(22, QFont.Black))
        self.category_title.setTextColor(HiveColor.FG)
        cl.addWidget(self.category_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        cl.addWidget(scroll)

        self.grid_widget = QWidget()
        self.grid_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.grid_widget)

        self.v_splitter.addWidget(center)

        # Console
        console_wrap = ShadowFrame(self, border_color=HiveColor.CYAN, bg_color=HiveColor.MUTED,
                                   shadow_layers=[(HiveColor.YELLOW, 8), (HiveColor.MAGENTA, 16)],
                                   radius=24, border_width=4)
        cwl = QVBoxLayout(console_wrap)
        cwl.setContentsMargins(12, 12, 12, 12)
        cwl.setSpacing(10)

        console_header = QHBoxLayout()
        console_title = ShadowLabel("◈ Output", shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        console_title.setFont(font_heading(11, QFont.Black))
        console_title.setTextColor(HiveColor.TEXT_SECONDARY)
        console_header.addWidget(console_title)
        console_header.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(30)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {HiveColor.MUTED.name()};
                border: 3px solid {HiveColor.MAGENTA.name()};
                border-radius: 9999px;
                padding: 2px 12px;
                color: {HiveColor.MAGENTA.name()};
                font-size: 8pt;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {HiveColor.MAGENTA.name()};
                color: {HiveColor.BG.name()};
            }}
        """)
        console_header.addWidget(clear_btn)
        cwl.addLayout(console_header)

        self.console = ConsoleWidget()
        self.console.setMinimumHeight(120)
        cwl.addWidget(self.console)
        clear_btn.clicked.connect(self.console.clear_log)

        self.v_splitter.addWidget(console_wrap)
        self.v_splitter.setSizes([560, 220])

        self.h_splitter.addWidget(center_stack)

        # Right: detail panel
        self.detail = ToolPanel()
        self.detail.run_tool.connect(self._run_tool)
        self.detail.run_tool_stop_requested.connect(self.runner.cancel)
        self.h_splitter.addWidget(self.detail)

        self.h_splitter.setSizes([760, 300])

        # Floating decorations
        self._spawn_floaters(center)

        # Initial selection
        if self._category_buttons:
            self._category_buttons[0].setChecked(True)
            self._select_category(self.registry.categories[0]["id"])

        self._log("BeeHive GUI ready. Select a tool and hit Run.", "accent")

    def _spawn_floaters(self, parent):
        emojis = ["🐝", "🍯", "⬡", "✦", "❋"]
        colors = HiveColor.ACCENTS
        for i in range(10):
            f = Floater(random.choice(emojis), size=random.randint(18, 34),
                        color=colors[i % len(colors)], parent=parent)
            f.move(random.randint(20, parent.width() - 40),
                   random.randint(20, parent.height() - 40))
            self._floaters.append(f)

    def _apply_window_shape(self):
        if self.isMaximized():
            self.clearMask()
            return
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(rect, 12, 12)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_window_shape()
        # Update pattern overlays
        for pt in [self.pt_comb, getattr(self, "_sb_pattern", None)]:
            if pt and pt.parent():
                pt.setGeometry(pt.parent().rect())
        if hasattr(self, "bg_text") and self.bg_text.parent():
            self.bg_text.setGeometry(self.bg_text.parent().rect())
        # Reposition floaters
        if hasattr(self, "_floaters"):
            for f in self._floaters:
                if f.parent():
                    f.move(random.randint(20, max(40, f.parent().width() - 40)),
                           random.randint(20, max(40, f.parent().height() - 40)))
        if hasattr(self, "grid_layout"):
            self._filter_tools(self.search.text())

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            self._apply_window_shape()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _select_category(self, cat_id: str):
        self._current_category = cat_id
        for i, cat in enumerate(self.registry.categories):
            self._category_buttons[i].setChecked(cat["id"] == cat_id)
        self.settings_btn.setChecked(False)
        self.about_btn.setChecked(False)

        cat_info = next(c for c in self.registry.categories if c["id"] == cat_id)
        self.category_title.setText(cat_info["name"])
        self.category_title.setTextColor(accent(self.registry.categories.index(cat_info)))
        self._filter_tools(self.search.text())

    def _filter_tools(self, text: str):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        text = text.lower()
        cat_info = next(c for c in self.registry.categories if c["id"] == self._current_category)
        tools = self.registry.tools.get(self._current_category, [])
        filtered = [t for t in tools if text in t["name"].lower() or text in t["desc"].lower()]

        cols = max(1, self._grid_columns())
        for i, tool in enumerate(filtered):
            idx = self.registry.categories.index(cat_info)
            card = ToolCard(tool["name"], tool["desc"], cat_info["color"], cat_info["icon"], index=i + idx * 10)
            card.setToolTip(tool["desc"])
            card.clicked.connect(partial(self._select_tool, tool, cat_info["color"]))
            self.grid_layout.addWidget(card, i // cols, i % cols)

        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 0)
        self.grid_layout.setColumnStretch(cols, 1)

    def _grid_columns(self) -> int:
        try:
            avail = self.grid_widget.parentWidget().width() - 60
        except Exception:
            avail = 760
        card_width = 246
        return max(1, avail // card_width)

    def _select_tool(self, tool: dict, accent_color: str):
        self.detail.set_tool(tool, accent_color)

    def _run_tool(self, handler, args, kwargs):
        tool = self.detail.current_tool
        if tool and self._current_category == "web":
            dlg = FloodDialog(tool, self._settings, self)
            dlg.run_flood.connect(self._run_flood_direct)
            dlg.exec()
            return

        self.console.clear_log()
        self._log(f"Running: {tool['name']}", "accent")
        self.runner.run(handler, args, kwargs)

    def _run_flood_direct(self, target, kwargs):
        self.console.clear_log()
        self._log(f"Deploying swarm: {self.detail.current_tool['name']}", "accent")
        self.runner.run(target, (), kwargs)

    def _on_started(self):
        self.detail.set_running(True)

    def _on_output(self, text: str):
        self.console.write(text)

    def _on_finished(self, ok: bool, msg: str):
        self.detail.set_running(False)
        if ok:
            self._log("Tool finished.", "success")
        else:
            self._log(f"Tool failed: {msg}", "error")

    def _on_request_input(self, label: str, default: str):
        dlg = AskDialog(label, default, self)
        if dlg.exec() == QDialog.Accepted:
            self.runner.provide_input(dlg.answer)
        else:
            self.runner.provide_input("")

    def _on_request_pause(self):
        dlg = PauseDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.runner.acknowledge_pause()
        else:
            self.runner.acknowledge_pause()

    def _show_settings(self):
        for btn in self._category_buttons:
            btn.setChecked(False)
        self.about_btn.setChecked(False)
        self.settings_btn.setChecked(True)

        container = ShadowFrame(self, border_color=HiveColor.MAGENTA, bg_color=HiveColor.BG,
                                shadow_layers=[(HiveColor.YELLOW, 10), (HiveColor.CYAN, 20)],
                                radius=24, border_width=4)
        dlg = QDialog(self, Qt.Dialog | Qt.FramelessWindowHint)
        dlg.setAttribute(Qt.WA_TranslucentBackground)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setMinimumSize(560, 480)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(0, 0, 0, 0)
        panel = SettingsPanel(self._settings)
        panel.theme_changed.connect(self._set_theme)
        panel.settings_saved.connect(lambda: self._log("Settings saved.", "success"))
        inner.addWidget(panel)

        dlg.exec()
        self.settings_btn.setChecked(False)
        if self._current_category:
            self._select_category(self._current_category)

    def _show_about(self):
        for btn in self._category_buttons:
            btn.setChecked(False)
        self.settings_btn.setChecked(False)
        self.about_btn.setChecked(True)

        total = sum(len(v) for v in self.registry.tools.values())
        QMessageBox.about(
            self, "About BeeHive",
            f"<h2 style='color:{HiveColor.YELLOW.name()}; text-shadow: 2px 2px 0 {HiveColor.MAGENTA.name()}, 4px 4px 0 {HiveColor.CYAN.name()};'>◈ BeeHive</h2>"
            f"<p style='color:{HiveColor.FG.name()};'>Honey-themed multi-tool launcher.</p>"
            f"<p style='color:{HiveColor.TEXT_SECONDARY.name()};'>Categories: {len(self.registry.categories)}<br>"
            f"Tools: {total}</p>"
            f"<p style='color:{HiveColor.TEXT_SECONDARY.name()};'>GUI built with PySide6.</p>"
        )
        self.about_btn.setChecked(False)
        if self._current_category:
            self._select_category(self._current_category)

    def _set_theme(self, name: str):
        self._settings["theme"] = name
        apply_theme(QApplication.instance(), name)

    def _log(self, text: str, kind: str = "info"):
        self.console.log.emit(text, kind)

    def closeEvent(self, event):
        if self.runner.is_running():
            self.runner.cancel()
        event.accept()
