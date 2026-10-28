"""
main.py
Entry point — creates QApplication with dark palette and launches MainWindow.
"""
import sys
import os

# Make sure the package directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

from app import MainWindow


def _dark_palette() -> QPalette:
    pal = QPalette()
    base   = QColor("#111111")
    alt    = QColor("#141414")
    text   = QColor("#cccccc")
    bright = QColor("#ffffff")
    mid    = QColor("#1e1e1e")
    dark   = QColor("#0a0a0a")
    hilite = QColor("#1D9E75")

    pal.setColor(QPalette.ColorRole.Window,          base)
    pal.setColor(QPalette.ColorRole.WindowText,      text)
    pal.setColor(QPalette.ColorRole.Base,            alt)
    pal.setColor(QPalette.ColorRole.AlternateBase,   mid)
    pal.setColor(QPalette.ColorRole.ToolTipBase,     mid)
    pal.setColor(QPalette.ColorRole.ToolTipText,     text)
    pal.setColor(QPalette.ColorRole.Text,            text)
    pal.setColor(QPalette.ColorRole.Button,          mid)
    pal.setColor(QPalette.ColorRole.ButtonText,      text)
    pal.setColor(QPalette.ColorRole.BrightText,      bright)
    pal.setColor(QPalette.ColorRole.Link,            hilite)
    pal.setColor(QPalette.ColorRole.Highlight,       hilite)
    pal.setColor(QPalette.ColorRole.HighlightedText, bright)
    pal.setColor(QPalette.ColorRole.Dark,            dark)
    pal.setColor(QPalette.ColorRole.Mid,             mid)
    pal.setColor(QPalette.ColorRole.Shadow,          dark)
    return pal


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vinyl Zoetrope Designer")
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())

    # Global stylesheet overrides for Fusion widgets
    app.setStyleSheet("""
        QToolTip {
            background: #1e1e1e; color: #ccc; border: 1px solid #333;
            border-radius: 4px; padding: 4px 8px;
        }
        QScrollBar:vertical {
            background: #111; width: 8px; border: none;
        }
        QScrollBar::handle:vertical {
            background: #2a2a2a; border-radius: 4px; min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #333; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QScrollBar:horizontal {
            background: #111; height: 8px; border: none;
        }
        QScrollBar::handle:horizontal {
            background: #2a2a2a; border-radius: 4px; min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover { background: #333; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        QSlider::groove:horizontal {
            background: #252525; height: 4px; border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #1D9E75; width: 14px; height: 14px;
            margin: -5px 0; border-radius: 7px;
        }
        QSlider::sub-page:horizontal { background: #1D9E75; border-radius: 2px; }
        QCheckBox::indicator {
            width: 14px; height: 14px;
            background: #1e1e1e; border: 1px solid #333; border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background: #1D9E75; border-color: #1D9E75;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
