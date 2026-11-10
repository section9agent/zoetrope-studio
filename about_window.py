"""
about_window.py
About dialog — credits, open-source acknowledgements, donation link.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)

from version import APP_VERSION

PAYPAL_URL = (
    "https://www.paypal.com/donate/?business=section9agent%40hotmail.com"
    "&currency_code=USD"
)

OSS_CREDITS = [
    ("Python",        "3.x",   "PSF License",           "https://python.org"),
    ("PyQt6",         "6.x",   "GPL v3 / Commercial",   "https://riverbankcomputing.com/software/pyqt/"),
    ("Qt",            "6.x",   "LGPL v3",               "https://qt.io"),
    ("Pillow (PIL)",  "10.x",  "HPND License",          "https://python-pillow.org"),
    ("PyInstaller",   "6.x",   "GPL v2 + bootloader exception", "https://pyinstaller.org"),
]


def _link_btn(label: str, url: str, color: str = "#378ADD") -> QPushButton:
    btn = QPushButton(label)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFlat(True)
    btn.setStyleSheet(f"""
        QPushButton {{
            color: {color}; border: none; font-size: 12px;
            text-decoration: underline; padding: 0; background: transparent;
        }}
        QPushButton:hover {{ color: #fff; }}
    """)
    btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
    return btn


class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Zoetrope Studio")
        self.setFixedSize(480, 560)
        self.setModal(True)
        self.setStyleSheet("background: #111; color: #ccc;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(0)

        # ── App name & version ───────────────────────────────────────
        name_lbl = QLabel("Zoetrope Studio")
        name_lbl.setStyleSheet(
            "color: #fff; font-size: 22px; font-weight: 700; letter-spacing: 1px;"
        )
        layout.addWidget(name_lbl)

        ver_lbl = QLabel(f"Version {APP_VERSION}")
        ver_lbl.setStyleSheet("color: #555; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(ver_lbl)

        layout.addSpacing(10)

        # ── Tagline ──────────────────────────────────────────────────
        tag = QLabel(
            "Design zoetrope animation strips for vinyl records.\n"
            "Drop GIFs or images, preview the strobe illusion,\n"
            "and export a print-ready disc."
        )
        tag.setStyleSheet("color: #888; font-size: 12px; line-height: 1.6;")
        tag.setWordWrap(True)
        layout.addWidget(tag)

        layout.addSpacing(16)
        layout.addWidget(self._divider())
        layout.addSpacing(12)

        # ── Credits ──────────────────────────────────────────────────
        credit_lbl = QLabel("CODED BY")
        credit_lbl.setStyleSheet(
            "color: #444; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        layout.addWidget(credit_lbl)
        layout.addSpacing(4)

        authors = QLabel("Claude (Anthropic)  &  Emmanuel Hoachlander")
        authors.setStyleSheet(
            "color: #1D9E75; font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(authors)

        layout.addSpacing(16)
        layout.addWidget(self._divider())
        layout.addSpacing(12)

        # ── Open source credits ──────────────────────────────────────
        oss_lbl = QLabel("OPEN SOURCE COMPONENTS")
        oss_lbl.setStyleSheet(
            "color: #444; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        layout.addWidget(oss_lbl)
        layout.addSpacing(8)

        for lib, ver, lic, url in OSS_CREDITS:
            row = QHBoxLayout()
            row.setSpacing(0)

            link = _link_btn(f"{lib} {ver}", url, "#378ADD")
            row.addWidget(link)
            row.addSpacing(8)

            lic_lbl = QLabel(f"— {lic}")
            lic_lbl.setStyleSheet("color: #555; font-size: 11px;")
            row.addWidget(lic_lbl)
            row.addStretch()

            layout.addLayout(row)
            layout.addSpacing(3)

        layout.addSpacing(16)
        layout.addWidget(self._divider())
        layout.addSpacing(14)

        # ── Donation ─────────────────────────────────────────────────
        donate_hdr = QLabel("SUPPORT THIS PROJECT")
        donate_hdr.setStyleSheet(
            "color: #444; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        layout.addWidget(donate_hdr)
        layout.addSpacing(6)

        donate_msg = QLabel(
            "If you enjoy Zoetrope Studio, please consider a donation.\n"
            "It helps keep the project alive and growing!"
        )
        donate_msg.setStyleSheet("color: #888; font-size: 12px;")
        donate_msg.setWordWrap(True)
        layout.addWidget(donate_msg)
        layout.addSpacing(10)

        donate_btn = QPushButton("💛  Donate via PayPal")
        donate_btn.setFixedHeight(38)
        donate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        donate_btn.setStyleSheet("""
            QPushButton {
                background: #003087; color: #fff; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 600;
            }
            QPushButton:hover { background: #0040b0; }
            QPushButton:pressed { background: #002060; }
        """)
        donate_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(PAYPAL_URL))
        )
        layout.addWidget(donate_btn)

        layout.addStretch()

        # ── Close button ─────────────────────────────────────────────
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888; border: 1px solid #2a2a2a;
                border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { background: #252525; color: #ccc; border-color: #333; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _divider(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("color: #1e1e1e; background: #1e1e1e; border: none; max-height: 1px;")
        return f
