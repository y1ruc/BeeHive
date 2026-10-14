"""
BeeHive GUI — application entry point.

Run with:
    python gui.py
or
    python -m gui
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import apply_theme


def main():
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("BeeHive")
    app.setApplicationDisplayName("BeeHive")
    app.setOrganizationName("beehive")

    # Start with honey theme; main_window will reload settings and switch if needed.
    apply_theme(app, "honey")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
