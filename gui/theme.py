"""BeeHive GUI - dark hand-drawn hive design tokens and Qt stylesheet."""

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette


class HiveColor:
    """The UI deliberately stays in the colours found inside a real hive."""

    BG = QColor("#100d08")
    SURFACE = QColor("#1b140c")
    PANEL = QColor("#271b0e")
    PANEL_RAISED = QColor("#342411")
    FG = QColor("#fff1c9")
    TEXT_PRIMARY = FG
    TEXT_SECONDARY = QColor("#d7bd82")
    TEXT_DISABLED = QColor("#8d754f")

    GOLD = QColor("#ffc64d")
    HONEY = QColor("#e89a16")
    AMBER = QColor("#b9670d")
    WAX = QColor("#f8d77a")
    COCOA = QColor("#4c2f14")
    BARK = QColor("#241609")
    DANGER = QColor("#c95632")
    INK = QColor("#080604")

    # Compatibility aliases used by the existing component API. Each resolves
    # to a bee-hive material, rather than the superseded neon palette.
    MUTED = PANEL
    BORDER = HONEY
    MAGENTA = HONEY
    CYAN = WAX
    YELLOW = GOLD
    ORANGE = AMBER
    PURPLE = COCOA

    ACCENTS = [HONEY, GOLD, WAX, AMBER, COCOA]
    SUCCESS = WAX
    WARNING = GOLD
    ERROR = DANGER
    INFO = HONEY


def accent(index: int) -> QColor:
    return HiveColor.ACCENTS[index % len(HiveColor.ACCENTS)]


def clash(index: int) -> QColor:
    """A deliberately different but still hive-native accent."""
    return accent(index + 2)


THEMES = {
    "honey": {"bg": HiveColor.BG, "panel": HiveColor.PANEL, "accent": HiveColor.HONEY},
    "dusk": {"bg": QColor("#15100b"), "panel": QColor("#291a0d"), "accent": QColor("#d98b13")},
    "smoke": {"bg": QColor("#12100c"), "panel": QColor("#242017"), "accent": QColor("#d2a342")},
}


def load_fonts():
    # Generic family names survive both a regular Windows launch and Qt's
    # off-screen renderer; decorative fonts are not guaranteed to ship there.
    return {"heading": "Sans Serif", "body": "Sans Serif", "display": "Sans Serif", "mono": "Monospace"}


FONTS = None


def get_fonts():
    global FONTS
    if FONTS is None:
        FONTS = load_fonts()
    return FONTS


def font_heading(size=10, weight=QFont.Bold):
    font = QFont(get_fonts()["heading"], size)
    font.setWeight(weight)
    return font


def font_body(size=10, weight=QFont.Normal):
    font = QFont(get_fonts()["body"], size)
    font.setWeight(weight)
    return font


def font_display(size=10, weight=QFont.Bold):
    font = QFont(get_fonts()["display"], size)
    font.setWeight(weight)
    return font


def font_mono(size=10, weight=QFont.Normal):
    font = QFont(get_fonts()["mono"], size)
    font.setWeight(weight)
    return font


def with_alpha(color: QColor, alpha: float) -> str:
    """Return a stable Qt stylesheet colour (QSS does not accept rgba everywhere)."""
    _ = alpha
    return QColor(color).name()


def _q(color: QColor) -> str:
    return color.name()


def stylesheet(theme_name="honey") -> str:
    theme = THEMES.get(theme_name, THEMES["honey"])
    bg, panel, primary = _q(theme["bg"]), _q(theme["panel"]), _q(theme["accent"])
    ink, gold, wax = _q(HiveColor.INK), _q(HiveColor.GOLD), _q(HiveColor.WAX)
    raised, text, disabled = _q(HiveColor.PANEL_RAISED), _q(HiveColor.FG), _q(HiveColor.TEXT_DISABLED)
    danger = _q(HiveColor.DANGER)

    return f"""
    QWidget {{
        background-color: {bg}; color: {text}; font-family: \"{get_fonts()['body']}\";
        font-size: 10pt; outline: none;
    }}
    QMainWindow, QDialog {{ background-color: {bg}; }}

    QScrollBar:vertical {{ background: {panel}; width: 12px; margin: 6px 0; }}
    QScrollBar::handle:vertical {{ background: {primary}; min-height: 36px; border: 2px solid {ink}; border-radius: 6px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: {panel}; height: 12px; margin: 0 6px; }}
    QScrollBar::handle:horizontal {{ background: {primary}; min-width: 36px; border: 2px solid {ink}; border-radius: 6px; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {raised}; border: 3px solid {HiveColor.COCOA.name()};
        border-radius: 13px 6px 12px 7px; padding: 8px 12px; color: {text};
        selection-background-color: {primary}; selection-color: {ink};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border-color: {gold}; background-color: {HiveColor.PANEL_RAISED.name()};
    }}
    QLineEdit::placeholder, QTextEdit::placeholder {{ color: {disabled}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background: {panel}; border: 3px solid {primary}; color: {text};
        selection-background-color: {primary}; selection-color: {ink};
    }}
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 0; border: 0; }}

    QPushButton {{
        background-color: {raised}; border: 3px solid {HiveColor.COCOA.name()};
        border-radius: 14px 7px 13px 8px; padding: 8px 16px; color: {text}; font-weight: 700;
    }}
    QPushButton:hover {{ background-color: {primary}; color: {ink}; border-color: {gold}; }}
    QPushButton:pressed {{ background-color: {gold}; color: {ink}; padding: 10px 14px 6px 18px; }}
    QPushButton:disabled {{ background-color: {panel}; color: {disabled}; border-color: {HiveColor.BARK.name()}; }}
    QPushButton#primary {{ background-color: {primary}; color: {ink}; border: 3px solid {gold}; font-weight: 800; }}
    QPushButton#primary:hover {{ background-color: {gold}; border-color: {wax}; }}
    QPushButton#danger {{ background-color: {danger}; color: {text}; border-color: {HiveColor.BARK.name()}; }}
    QPushButton#danger:hover {{ background-color: {HiveColor.DANGER.lighter(120).name()}; border-color: {gold}; }}

    QCheckBox, QRadioButton {{ spacing: 8px; color: {text}; }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px; height: 18px; background: {raised}; border: 2px solid {HiveColor.COCOA.name()};
    }}
    QCheckBox::indicator {{ border-radius: 5px 2px 5px 2px; }}
    QRadioButton::indicator {{ border-radius: 9px; }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ background: {primary}; border-color: {gold}; }}

    QGroupBox {{
        border: 3px dashed {HiveColor.COCOA.name()}; border-radius: 18px 8px 15px 10px;
        margin-top: 16px; padding: 16px; color: {wax}; font-weight: 700;
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 14px; padding: 0 7px; }}
    QSplitter::handle {{ background: {HiveColor.BARK.name()}; }}
    QSplitter::handle:horizontal {{ width: 8px; }}
    QSplitter::handle:vertical {{ height: 8px; }}
    QMenu {{ background: {panel}; border: 3px solid {primary}; border-radius: 10px; padding: 6px; }}
    QMenu::item {{ padding: 7px 18px; border-radius: 8px 3px 8px 3px; }}
    QMenu::item:selected {{ background: {primary}; color: {ink}; }}
    QToolTip {{ background: {HiveColor.INK.name()}; color: {wax}; border: 2px solid {primary}; padding: 6px; }}
    """


def apply_theme(app, theme_name="honey"):
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet(theme_name))
    theme = THEMES.get(theme_name, THEMES["honey"])
    palette = app.palette()
    palette.setColor(QPalette.Window, theme["bg"])
    palette.setColor(QPalette.WindowText, HiveColor.FG)
    palette.setColor(QPalette.Base, theme["panel"])
    palette.setColor(QPalette.AlternateBase, HiveColor.PANEL_RAISED)
    palette.setColor(QPalette.Text, HiveColor.FG)
    palette.setColor(QPalette.Button, HiveColor.PANEL_RAISED)
    palette.setColor(QPalette.ButtonText, HiveColor.FG)
    palette.setColor(QPalette.Highlight, theme["accent"])
    palette.setColor(QPalette.HighlightedText, HiveColor.INK)
    app.setPalette(palette)
