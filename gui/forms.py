"""
BeeHive GUI — Dedicated tool forms (Maximalist edition).
"""

import os

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout,
)

from .components import ShadowFrame, ShadowLabel
from .theme import HiveColor, accent, clash, font_body, font_display, font_heading


# ---------------------------------------------------------------------------
# Flood form
# ---------------------------------------------------------------------------

class FloodDialog(QDialog):
    run_flood = Signal(object, dict)

    def __init__(self, tool: dict, settings: dict, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(460)
        self.tool = tool
        self.settings = settings
        self._build()

    def _build(self):
        container = ShadowFrame(self, border_color=HiveColor.MAGENTA, bg_color=HiveColor.MUTED,
                                shadow_layers=[(HiveColor.YELLOW, 10), (HiveColor.CYAN, 20)],
                                radius=24, border_width=4)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(24, 22, 24, 22)
        inner.setSpacing(16)

        title = ShadowLabel(f"◈  {self.tool['name']}", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
            (QPoint(4, 4), HiveColor.MAGENTA),
            (QPoint(6, 6), HiveColor.CYAN),
        ])
        title.setFont(font_display(18, QFont.Black))
        title.setTextColor(HiveColor.YELLOW)
        inner.addWidget(title)

        sub = QLabel(self.tool["desc"])
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {HiveColor.TEXT_SECONDARY.name()};")
        inner.addWidget(sub)

        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("game code or pin")
        self._row(inner, "Target", self.target_edit)

        self.bots_spin = QSpinBox()
        self.bots_spin.setRange(1, 5000)
        self.bots_spin.setValue(25)
        self._row(inner, "Bots", self.bots_spin)

        self.conc_spin = QSpinBox()
        self.conc_spin.setRange(1, 64)
        self.conc_spin.setValue(self.settings.get("concurrency", 8))
        self._row(inner, "Concurrency", self.conc_spin)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 10.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setValue(self.settings.get("delay", 0.0))
        self._row(inner, "Delay (s)", self.delay_spin)

        self.name_mode = QComboBox()
        self.name_mode.addItems(["prefix", "random", "file"])
        self.name_mode.setCurrentText(self.settings.get("name_mode", "prefix"))
        self.name_mode.currentTextChanged.connect(self._on_mode_changed)
        self._row(inner, "Name Mode", self.name_mode)

        self.prefix_edit = QLineEdit(self.settings.get("name_prefix", "Bee"))
        self.prefix_lbl, _ = self._row(inner, "Prefix", self.prefix_edit)

        file_row = QHBoxLayout()
        self.file_edit = QLineEdit(self.settings.get("name_file", ""))
        self.file_edit.setPlaceholderText("names.txt")
        self.file_btn = QPushButton("Browse")
        self.file_btn.setFixedWidth(80)
        self.file_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self.file_edit, 1)
        file_row.addWidget(self.file_btn)
        self.file_lbl = ShadowLabel("Name File", shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        self.file_lbl.setFont(font_heading(10, QFont.Black))
        self.file_lbl.setTextColor(HiveColor.TEXT_SECONDARY)
        self.file_lbl.setFixedWidth(100)
        row = QHBoxLayout()
        row.addWidget(self.file_lbl)
        row.addLayout(file_row, 1)
        inner.addLayout(row)

        self.answer_check = QCheckBox("Auto-answer questions")
        self.answer_check.setChecked(False)
        self._row(inner, "", self.answer_check)
        self.answer_check.setVisible("kahoot" in self.tool["name"].lower())

        inner.addSpacing(12)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        run = QPushButton("Deploy Swarm")
        run.setObjectName("primary")
        run.setFixedHeight(52)
        run.clicked.connect(self._on_run)
        btns.addWidget(cancel)
        btns.addWidget(run)
        inner.addLayout(btns)

        self._on_mode_changed(self.name_mode.currentText())

    def _row(self, layout, label: str, widget):
        row = QHBoxLayout()
        lbl = ShadowLabel(label, shadows=[(QPoint(1, 1), HiveColor.PURPLE)])
        lbl.setFont(font_heading(10, QFont.Black))
        lbl.setTextColor(HiveColor.TEXT_SECONDARY)
        lbl.setFixedWidth(100)
        row.addWidget(lbl)
        if isinstance(widget, QHBoxLayout):
            row.addLayout(widget, 1)
        else:
            row.addWidget(widget, 1)
        layout.addLayout(row)
        return lbl, row

    def _on_mode_changed(self, mode: str):
        self.prefix_edit.setEnabled(mode == "prefix")
        self.file_edit.setEnabled(mode == "file")
        self.file_btn.setEnabled(mode == "file")

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Name File", "", "Text Files (*.txt)")
        if path:
            self.file_edit.setText(path)

    def _resolve_names(self):
        mode = self.name_mode.currentText()
        if mode == "random":
            return {"use_random": True}
        if mode == "file":
            return {"name_file": self.file_edit.text()}
        return {"prefix": self.prefix_edit.text() or "Bee"}

    def _on_run(self):
        code = self.target_edit.text().strip()
        if not code:
            return

        name_kw = self._resolve_names()
        kwargs = {
            "bots": self.bots_spin.value(),
            "concurrency": self.conc_spin.value(),
            "delay": self.delay_spin.value(),
            "bar": True,
        }
        kwargs.update(name_kw)

        handler = self.tool["handler"]
        name = self.tool["name"].lower()

        import beehive
        if "blooket" in name:
            kwargs["code"] = code
            target = beehive.blooket_flood
        elif "kahoot" in name:
            kwargs["pin"] = code
            kwargs["answer"] = self.answer_check.isChecked()
            target = beehive.kahoot.run_flood
        elif "quizizz" in name:
            kwargs["code"] = code
            target = beehive.site_flood(beehive.quizizz.join_one)
        elif "gimkit" in name:
            kwargs["code"] = code
            target = beehive.site_flood(beehive.gimkit.join_one)
        elif "menti" in name or "mentimeter" in name:
            kwargs["code"] = code
            target = beehive.site_flood(beehive.menti.join_one)
        elif "quizlet" in name:
            kwargs["code"] = code
            target = beehive.site_flood(beehive.quizletlive.join_one)
        else:
            kwargs["code"] = code
            target = handler

        self.run_flood.emit(target, kwargs)
        self.accept()
