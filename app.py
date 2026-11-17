"""
app.py
MainWindow — three-panel layout: ring manager | preview | settings.
Includes a Help menu with About and Check for Updates.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFrame, QSizePolicy, QCheckBox,
)

from record_model import RecordModel
from preview_widget import PreviewWidget
from ring_manager_widget import RingManagerWidget
from settings_widget import SettingsWidget
from about_window import AboutWindow
from updater import UpdateChecker


def _vline() -> QFrame:
    """A thin vertical separator line."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setStyleSheet("color: #222;")
    f.setFixedWidth(1)
    return f


def _panel(widget: QWidget, bg: str = "#111111") -> QWidget:
    """Wrap a widget in a padded container with a dark background."""
    container = QWidget()
    container.setStyleSheet(f"background: {bg};")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.addWidget(widget)
    return container


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoetrope Studio")
        self.setMinimumSize(1060, 720)
        self.resize(1200, 780)

        self._model  = RecordModel("12in")
        self._updater = UpdateChecker(self)
        self._build_ui()
        self._build_menu()

        # Background update check on launch (silent — only pops up if update found)
        self._updater.check(silent=True)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel: ring manager ─────────────────────────────────
        self._ring_mgr = RingManagerWidget(self._model)
        left = _panel(self._ring_mgr, "#0e0e0e")
        left.setFixedWidth(240)
        root.addWidget(left)
        root.addWidget(_vline())

        # ── Centre panel: preview ────────────────────────────────────
        self._preview = PreviewWidget(self._model)
        self._preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        centre = _panel(self._preview, "#111111")
        root.addWidget(centre, stretch=1)
        root.addWidget(_vline())

        # ── Right panel: settings ────────────────────────────────────
        self._settings = SettingsWidget(self._model)
        right = _panel(self._settings, "#0e0e0e")
        right.setFixedWidth(220)
        root.addWidget(right)

        # ── Wire signals ─────────────────────────────────────────────
        self._ring_mgr.ring_changed.connect(self._on_model_changed)
        self._settings.setting_changed.connect(self._on_model_changed)
        self._settings.model_changed.connect(self._on_record_type_changed)

    def _build_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #0d0d0d; color: #888;
                border-bottom: 1px solid #1e1e1e;
                font-size: 12px; padding: 2px 4px;
            }
            QMenuBar::item:selected { background: #1a1a1a; color: #ccc; border-radius: 4px; }
            QMenu {
                background: #141414; color: #ccc;
                border: 1px solid #252525; border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item { padding: 6px 24px; }
            QMenu::item:selected { background: #1D9E75; color: #fff; }
            QMenu::separator { height: 1px; background: #252525; margin: 4px 8px; }
        """)

        # ── Help menu ────────────────────────────────────────────────
        help_menu = menubar.addMenu("Help")

        act_check = QAction("Check for Updates…", self)
        act_check.triggered.connect(lambda: self._updater.check(silent=False))
        help_menu.addAction(act_check)

        # Auto-update toggle (checkable menu item)
        self._act_autoupdate = QAction("Auto-check for Updates on Launch", self)
        self._act_autoupdate.setCheckable(True)
        self._act_autoupdate.setChecked(self._updater.auto_update_enabled)
        self._act_autoupdate.toggled.connect(self._on_autoupdate_toggled)
        help_menu.addAction(self._act_autoupdate)

        help_menu.addSeparator()

        act_about = QAction("About Zoetrope Studio…", self)
        act_about.triggered.connect(self._on_about)
        help_menu.addAction(act_about)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_model_changed(self):
        """Called when rings or display settings change."""
        self._preview.refresh()
        self._ring_mgr._update_info_label()

    def _on_record_type_changed(self):
        """Called when 12"/7" toggle flips (clears rings, changes frame count)."""
        self._ring_mgr.set_model(self._model)
        self._preview.set_model(self._model)
        self._settings.set_model(self._model)

    def _on_about(self):
        dlg = AboutWindow(self)
        dlg.exec()

    def _on_autoupdate_toggled(self, checked: bool):
        self._updater.auto_update_enabled = checked
