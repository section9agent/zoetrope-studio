"""
app.py
MainWindow — three-panel layout: ring manager | preview | settings.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFrame, QSizePolicy,
)

from record_model import RecordModel
from preview_widget import PreviewWidget
from ring_manager_widget import RingManagerWidget
from settings_widget import SettingsWidget


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
        self.setWindowTitle("Vinyl Zoetrope Designer")
        self.setMinimumSize(1060, 720)
        self.resize(1200, 780)

        self._model = RecordModel("12in")
        self._build_ui()

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

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_model_changed(self):
        """Called when rings or display settings change."""
        self._preview.refresh()
        # Re-sync ring manager info (ring heights change as rings are added)
        self._ring_mgr._update_info_label()

    def _on_record_type_changed(self):
        """Called when 12"/7" toggle flips (clears rings, changes frame count)."""
        self._ring_mgr.set_model(self._model)
        self._preview.set_model(self._model)
        self._settings.set_model(self._model)
