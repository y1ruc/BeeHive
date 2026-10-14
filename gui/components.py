"""
BeeHive GUI — Maximalist UI components.
Thick borders, stacked shadows, rotating accents, patterns, floating shapes,
and deliberate visual chaos.
"""

import math
import random

from PySide6.QtCore import (
    QEasingCurve, QEvent, QPoint, QPointF, QPropertyAnimation, QRectF,
    QSequentialAnimationGroup, QSize, Qt, Signal,
)
from PySide6.QtGui import (
    QColor, QFont, QFontMetrics, QLinearGradient, QMouseEvent, QPainter,
    QPainterPath, QPaintEvent, QPen, QPixmap, QRegion,
)
from PySide6.QtWidgets import (
    QAbstractButton, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
)

from .theme import (
    HiveColor, accent, clash, font_body, font_display, font_heading, font_mono,
    with_alpha,
)


# ---------------------------------------------------------------------------
# Text-shadow label
# ---------------------------------------------------------------------------

class ShadowLabel(QLabel):
    """A QLabel that paints text with a stacked shadow."""

    def __init__(self, text="", parent=None, shadows=None, gradient=False):
        super().__init__(text, parent)
        self.shadows = shadows or [(QPoint(2, 2), HiveColor.BARK)]
        self.gradient = gradient
        self._base_color = HiveColor.FG

    def setTextColor(self, color: QColor):
        self._base_color = color
        self.update()

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        text = self.text()
        flags = self.alignment()
        font = self.font()
        rect = self.rect()

        # Measure
        fm = QFontMetrics(font)
        bounding = fm.boundingRect(rect, flags, text)

        if self.gradient:
            grad = QLinearGradient(bounding.topLeft(), bounding.bottomRight())
            grad.setColorAt(0, HiveColor.MAGENTA)
            grad.setColorAt(0.35, HiveColor.CYAN)
            grad.setColorAt(0.7, HiveColor.YELLOW)
            grad.setColorAt(1, HiveColor.MAGENTA)
            base_color = grad
        else:
            base_color = self._base_color

        # Draw shadows
        for offset, color in self.shadows:
            shadow_rect = bounding.adjusted(offset.x(), offset.y(), offset.x(), offset.y())
            p.setPen(color)
            p.setFont(font)
            p.drawText(shadow_rect, flags, text)

        # Draw main text
        p.setFont(font)
        if isinstance(base_color, QLinearGradient):
            p.setPen(QPen(base_color, 1))
        else:
            p.setPen(base_color)
        p.drawText(bounding, flags, text)
        p.end()


# ---------------------------------------------------------------------------
# Multi-shadow frame base
# ---------------------------------------------------------------------------

class ShadowFrame(QFrame):
    """Frame with stacked hard shadows drawn manually."""

    def __init__(self, parent=None, border_color=None, bg_color=None,
                 shadow_layers=None, radius=24, border_width=4):
        super().__init__(parent)
        self.border_color = border_color or HiveColor.HONEY
        self.bg_color = bg_color or HiveColor.PANEL
        self.shadow_layers = shadow_layers or [(HiveColor.BARK, 7)]
        self.radius = radius
        self.border_width = border_width

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Solid cut-paper shadow: intentionally hard, never blurred.
        for color, offset in self.shadow_layers:
            rect = self.rect().adjusted(self.border_width, self.border_width,
                                        -self.border_width - offset, -self.border_width - offset)
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect.translated(offset, offset), self.radius, self.radius)

        # Draw background
        rect = self.rect().adjusted(self.border_width, self.border_width,
                                    -self.border_width, -self.border_width)
        p.setBrush(self.bg_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(rect, self.radius, self.radius)

        # Draw border
        pen = QPen(self.border_color, self.border_width)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        border_rect = self.rect().adjusted(self.border_width / 2, self.border_width / 2,
                                           -self.border_width / 2, -self.border_width / 2)
        p.drawRoundedRect(border_rect, self.radius, self.radius)
        p.end()


# ---------------------------------------------------------------------------
# Pattern background
# ---------------------------------------------------------------------------

class PatternBackground(QWidget):
    def __init__(self, parent=None, pattern="dots", color=None, density=20):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.pattern = pattern
        self.color = color or HiveColor.MAGENTA
        self.density = density
        self._opacity = 0.12

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self.color)
        c.setAlphaF(self._opacity)

        if self.pattern in ("comb", "dots", "stripes", "mesh"):
            # Offset hexagons make the hive reference visible without making
            # the work surface noisy.
            radius = max(7, self.density // 2)
            pen = QPen(c)
            pen.setWidth(1)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            step_x = int(math.sqrt(3) * radius)
            step_y = int(1.5 * radius)
            for row, y in enumerate(range(-radius, self.height() + radius, step_y)):
                x_offset = 0 if row % 2 == 0 else step_x // 2
                for x in range(-step_x, self.width() + step_x, step_x):
                    center = QPointF(x + x_offset, y)
                    points = [
                        QPointF(center.x() + radius * math.cos(math.radians(60 * point - 30)),
                                center.y() + radius * math.sin(math.radians(60 * point - 30)))
                        for point in range(6)
                    ]
                    path = QPainterPath()
                    path.addPolygon(points)
                    p.drawPath(path)
        elif self.pattern == "checker":
            c2 = QColor(self.color)
            c2.setAlphaF(self._opacity * 0.6)
            step = self.density
            for y in range(0, self.height(), step):
                for x in range(0, self.width(), step):
                    if ((x // step) + (y // step)) % 2 == 0:
                        p.fillRect(x, y, step, step, c)
                    else:
                        p.fillRect(x, y, step, step, c2)
        elif self.pattern == "mesh":
            for i, col in enumerate([HiveColor.MAGENTA, HiveColor.CYAN, HiveColor.PURPLE]):
                cc = QColor(col)
                cc.setAlphaF(0.08 + i * 0.03)
                cx = [0.2, 0.8, 0.5][i]
                cy = [0.3, 0.7, 0.5][i]
                rx = self.width() * 0.6
                ry = self.height() * 0.6
                p.setBrush(cc)
                p.setPen(Qt.NoPen)
                p.drawEllipse(int(self.width() * cx - rx / 2),
                              int(self.height() * cy - ry / 2),
                              int(rx), int(ry))
        p.end()


# ---------------------------------------------------------------------------
# Floating decorative shape
# ---------------------------------------------------------------------------

class Floater(QLabel):
    """A floating emoji/shape with a gentle bob animation."""

    def __init__(self, char: str, size: int = 24, color=None, parent=None):
        super().__init__(char, parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFixedSize(size + 8, size + 8)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(font_display(size, QFont.Bold))
        self.setStyleSheet(f"color: {(color or HiveColor.YELLOW).name()}; background: transparent; border: none;")

        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(3000 + random.randint(0, 2000))
        self._anim.setStartValue(self.pos())
        end = self.pos() + QPoint(0, -15 if random.random() > 0.5 else 15)
        self._anim.setEndValue(end)
        self._anim.setEasingCurve(QEasingCurve.InOutSine)
        self._anim.finished.connect(self._reverse)
        self._anim.start()

    def _reverse(self):
        v = self._anim.startValue()
        self._anim.setStartValue(self._anim.endValue())
        self._anim.setEndValue(v)
        self._anim.start()


# ---------------------------------------------------------------------------
# Frameless title bar
# ---------------------------------------------------------------------------

class TitleBar(QFrame):
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent=None, title="BeeHive"):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(48)
        self.setObjectName("titleBar")
        self.setStyleSheet(f"""
            #titleBar {{
                background-color: {HiveColor.MUTED.name()};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 4px dashed {HiveColor.CYAN.name()};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        self.icon = ShadowLabel("◈", shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
        ])
        self.icon.setFont(font_display(16, QFont.Bold))
        self.icon.setStyleSheet(f"color: {HiveColor.YELLOW.name()}; background: transparent; border: none;")
        self.icon.setFixedWidth(28)
        layout.addWidget(self.icon)

        self.title = ShadowLabel(title, shadows=[
            (QPoint(1, 1), HiveColor.PURPLE),
            (QPoint(2, 2), HiveColor.MAGENTA),
        ])
        self.title.setFont(font_heading(11, QFont.Black))
        self.title.setStyleSheet(f"color: {HiveColor.FG.name()}; background: transparent; border: none;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.btn_min = self._win_btn("−", HiveColor.CYAN)
        self.btn_max = self._win_btn("□", HiveColor.YELLOW)
        self.btn_close = self._win_btn("×", HiveColor.MAGENTA)

        self.btn_min.clicked.connect(self.minimize_clicked.emit)
        self.btn_max.clicked.connect(self.maximize_clicked.emit)
        self.btn_close.clicked.connect(self.close_clicked.emit)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def _win_btn(self, text, color):
        btn = QPushButton(text)
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {HiveColor.MUTED.name()};
                border: 3px solid {color.name()};
                border-radius: 9999px;
                color: {color.name()};
                font-size: 14px;
                font-weight: 900;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {color.name()};
                color: {HiveColor.BG.name()};
            }}
        """)
        return btn

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()


# ---------------------------------------------------------------------------
# Sidebar category button
# ---------------------------------------------------------------------------

class CategoryButton(QAbstractButton):
    def __init__(self, icon_text, label, accent, index=0, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label
        # Tool metadata used to carry a neon colour. The navigation palette is
        # intentionally normalised to hive materials.
        self.accent = HiveColor.ACCENTS[index % len(HiveColor.ACCENTS)]
        self.index = index
        self.clash = clash(index)
        self._hover = False
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._rotation = 0.5 if index % 2 == 0 else -0.5
        self._hover_rotation = self._rotation * 2

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Stacked hard shadow
        rect = self.rect().adjusted(4, 2, -4, -2)
        p.setPen(Qt.NoPen)
        p.setBrush(HiveColor.BARK)
        p.drawRoundedRect(rect.translated(5, 5), 14, 14)

        # Background
        if self.isChecked():
            bg = HiveColor.HONEY
            border = HiveColor.GOLD
            text_color = HiveColor.INK
        elif self._hover:
            bg = HiveColor.PANEL_RAISED
            border = HiveColor.HONEY
            text_color = HiveColor.FG
        else:
            bg = HiveColor.PANEL
            border = HiveColor.COCOA
            text_color = HiveColor.TEXT_SECONDARY

        p.setBrush(bg)
        p.setPen(QPen(border, 4))
        p.drawRoundedRect(rect, 14, 14)

        # Text with slight rotation
        p.save()
        center = rect.center()
        rot = self._hover_rotation if self._hover else self._rotation
        p.translate(center)
        p.rotate(rot)
        p.translate(-center)

        p.setPen(text_color)
        p.setFont(font_display(13, QFont.Black))
        p.drawText(rect.adjusted(14, 0, 0, 0), Qt.AlignVCenter | Qt.AlignLeft, self.icon_text)

        p.setFont(font_heading(10, QFont.Black))
        text_rect = rect.adjusted(42, 0, -10, 0)
        p.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.label_text)
        p.restore()

        # Accent notch
        if self.isChecked():
            p.setPen(Qt.NoPen)
            p.setBrush(self.accent)
            p.drawRoundedRect(rect.right() - 6, rect.center().y() - 10, 4, 20, 2, 2)

        p.end()

    def enterEvent(self, event: QEvent):
        self._hover = True
        self.update()

    def leaveEvent(self, event: QEvent):
        self._hover = False
        self.update()


# ---------------------------------------------------------------------------
# Tool card
# ---------------------------------------------------------------------------

class ToolCard(QFrame):
    clicked = Signal()

    def __init__(self, name, description, accent, icon="◈", index=0, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.accent = HiveColor.ACCENTS[index % len(HiveColor.ACCENTS)]
        self.icon = icon
        self.index = index
        self._hover = False
        self.setFixedSize(230, 130)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.NoFrame)
        self._rotation = 0.5 if index % 2 == 0 else -0.5
        self._clash = HiveColor.BARK

        self.setStyleSheet(f"""
            ToolCard {{
                background-color: transparent;
                border: none;
                border-radius: 24px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)
        self.icon_lbl = ShadowLabel(self.icon, shadows=[
            (QPoint(2, 2), HiveColor.PURPLE),
        ])
        self.icon_lbl.setFont(font_display(20, QFont.Black))
        self.icon_lbl.setTextColor(self.accent)
        self.icon_lbl.setFixedWidth(32)
        top.addWidget(self.icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        self.name_lbl = ShadowLabel(name, shadows=[
            (QPoint(1, 1), HiveColor.PURPLE),
            (QPoint(2, 2), self._clash),
        ])
        self.name_lbl.setFont(font_heading(11, QFont.Black))
        self.name_lbl.setTextColor(HiveColor.FG)
        layout.addWidget(self.name_lbl)

        self.desc_lbl = QLabel(description)
        self.desc_lbl.setFont(font_body(9))
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {HiveColor.TEXT_SECONDARY.name()};")
        layout.addWidget(self.desc_lbl)

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Stacked shadows
        rect = self.rect().adjusted(2, 2, -2, -2)
        p.setPen(Qt.NoPen)
        p.setBrush(HiveColor.BARK)
        p.drawRoundedRect(rect.translated(6, 6), 22, 22)

        # Card background
        p.setBrush(HiveColor.PANEL_RAISED)
        p.setPen(QPen(self.accent, 3))
        p.drawRoundedRect(rect, 22, 22)

        # Hover overlay
        if self._hover:
            over = QColor(self.accent)
            over.setAlphaF(0.12)
            p.setBrush(over)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(rect, 22, 22)

        p.end()

    def enterEvent(self, event: QEvent):
        self._hover = True
        self.update()

    def leaveEvent(self, event: QEvent):
        self._hover = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()


# ---------------------------------------------------------------------------
# Search box
# ---------------------------------------------------------------------------

class SearchBox(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search tools...")
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {HiveColor.PANEL_RAISED.name()};
                border: 3px solid {HiveColor.COCOA.name()};
                border-radius: 15px 7px 13px 8px;
                padding-left: 18px;
                color: {HiveColor.FG.name()};
                font-weight: bold;
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border: 3px solid {HiveColor.GOLD.name()};
                background-color: {HiveColor.PANEL_RAISED.name()};
            }}
        """)


# ---------------------------------------------------------------------------
# Console output widget
# ---------------------------------------------------------------------------

class ConsoleWidget(QTextEdit):
    log = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(font_mono(9))
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {HiveColor.INK.name()};
                border: 3px dashed {HiveColor.COCOA.name()};
                border-radius: 14px 7px 12px 8px;
                padding: 10px;
                color: {HiveColor.FG.name()};
            }}
        """)
        self.log.connect(self._append)

    def _append(self, text, kind="info"):
        color = {
            "info": HiveColor.FG.name(),
            "success": HiveColor.WAX.name(),
            "warning": HiveColor.GOLD.name(),
            "error": HiveColor.DANGER.name(),
            "accent": HiveColor.HONEY.name(),
        }.get(kind, HiveColor.FG.name())
        self.append(f'<span style="color:{color};white-space:pre-wrap;">{self._escape(text)}</span>')

    def _escape(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def write(self, text: str):
        if text:
            self.log.emit(text, "info")

    def flush(self):
        pass

    def clear_log(self):
        self.clear()
