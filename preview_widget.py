"""
preview_widget.py
The spinning record canvas with three playback modes:
  • Spin     — continuous rotation, no strobe effect
  • Freeze   — advances exactly 1/N rotation per 25 Hz tick (simulates eye under strobe)
  • Blink    — continuous spin but canvas flashes black at 25 Hz
"""
from __future__ import annotations
import math
import time

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QSizePolicy,
)

from record_model import RecordModel
from renderer import RecordRenderer


# ---------------------------------------------------------------------------
# Playback mode constants
# ---------------------------------------------------------------------------

MODE_STOPPED = "stopped"
MODE_SPIN    = "spin"
MODE_FREEZE  = "freeze"
MODE_BLINK   = "blink"

TIMER_INTERVAL_MS = 16          # ~60 fps render loop
STROBE_HZ         = 25.0        # persistence-of-vision flash rate


class PreviewWidget(QWidget):
    """Centre panel — spinning record canvas + transport controls."""

    def __init__(self, model: RecordModel, parent=None):
        super().__init__(parent)
        self.model    = model
        self.renderer = RecordRenderer()

        self._mode        = MODE_STOPPED
        self._angle_rad   = 0.0          # current disc rotation
        self._speed_mult  = 1.0
        self._last_ts     = None         # time.perf_counter() at last tick
        self._strobe_acc  = 0.0          # accumulator for strobe ticks (seconds)
        self._strobe_vis  = True         # strobe: is the frame visible?
        self._freeze_acc  = 0.0          # accumulator for freeze ticks

        self._canvas_size = 520          # square canvas pixels

        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Canvas label (QLabel used as image display)
        self._canvas = QLabel()
        self._canvas.setFixedSize(self._canvas_size, self._canvas_size)
        self._canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._canvas.setStyleSheet("background: #0a0a0a; border-radius: 260px; border: 1px solid #222;")
        layout.addWidget(self._canvas, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Transport buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._btn_spin   = self._make_btn("▶  Spin",   "#1D9E75", self._on_spin)
        self._btn_freeze = self._make_btn("❄  Freeze", "#378ADD", self._on_freeze)
        self._btn_blink  = self._make_btn("⚡  Blink",  "#EF9F27", self._on_blink)
        self._btn_stop   = self._make_btn("■  Stop",   "#555555", self._on_stop)

        for btn in (self._btn_spin, self._btn_freeze, self._btn_blink, self._btn_stop):
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

        # Speed row
        speed_row = QHBoxLayout()
        speed_row.setSpacing(8)
        speed_label = QLabel("Speed")
        speed_label.setStyleSheet("color: #666; font-size: 12px;")
        speed_row.addWidget(speed_label)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 30)   # 0.1× to 3.0× in 0.1 steps
        self._speed_slider.setValue(10)       # 1.0×
        self._speed_slider.setTickPosition(QSlider.TickPosition.NoTicks)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        speed_row.addWidget(self._speed_slider, stretch=1)

        self._speed_val_label = QLabel("1.0×")
        self._speed_val_label.setFixedWidth(36)
        self._speed_val_label.setStyleSheet("color: #ccc; font-size: 12px; font-weight: bold;")
        speed_row.addWidget(self._speed_val_label)

        self._rpm_label = QLabel()
        self._rpm_label.setStyleSheet(
            "color: #5DCAA5; background: #0a2e1e; border: 1px solid #1D9E75;"
            "border-radius: 10px; padding: 2px 10px; font-size: 11px;"
        )
        speed_row.addWidget(self._rpm_label)

        layout.addLayout(speed_row)
        self._update_rpm_label()
        self._refresh_canvas(black=False)

    def _make_btn(self, text: str, color: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedHeight(34)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e1e1e; color: #ccc;
                border: 1px solid #333; border-radius: 8px;
                font-size: 13px; font-weight: 500; padding: 0 12px;
            }}
            QPushButton:checked {{
                background: {color}; color: #fff; border-color: {color};
            }}
            QPushButton:hover:!checked {{
                background: #282828; border-color: #444; color: #fff;
            }}
        """)
        btn.clicked.connect(slot)
        return btn

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_model(self, model: RecordModel):
        self.model = model
        self._refresh_canvas(black=False)

    def refresh(self):
        """Called externally when the model changes (ring added/removed etc.)."""
        if self._mode == MODE_STOPPED:
            self._refresh_canvas(black=False)

    # ------------------------------------------------------------------
    # Transport slots
    # ------------------------------------------------------------------

    def _on_spin(self):
        self._set_mode(MODE_SPIN)

    def _on_freeze(self):
        self._set_mode(MODE_FREEZE)

    def _on_blink(self):
        self._set_mode(MODE_BLINK)

    def _on_stop(self):
        self._set_mode(MODE_STOPPED)

    def _set_mode(self, mode: str):
        self._mode = mode
        self._strobe_acc  = 0.0
        self._freeze_acc  = 0.0
        self._strobe_vis  = True
        self._last_ts     = None

        # Update button checked states
        self._btn_spin.setChecked(mode == MODE_SPIN)
        self._btn_freeze.setChecked(mode == MODE_FREEZE)
        self._btn_blink.setChecked(mode == MODE_BLINK)
        self._btn_stop.setChecked(mode == MODE_STOPPED)

        if mode == MODE_STOPPED:
            self._timer.stop()
            self._refresh_canvas(black=False)
        else:
            if not self._timer.isActive():
                self._timer.start(TIMER_INTERVAL_MS)

    # ------------------------------------------------------------------
    # Speed
    # ------------------------------------------------------------------

    def _on_speed_changed(self, value: int):
        self._speed_mult = value / 10.0
        self._speed_val_label.setText(f"{self._speed_mult:.1f}×")
        self._update_rpm_label()

    def _update_rpm_label(self):
        rpm = self.model.rpm * self._speed_mult
        self._rpm_label.setText(f"{rpm:.1f} RPM")

    # ------------------------------------------------------------------
    # Timer tick
    # ------------------------------------------------------------------

    def _tick(self):
        now = time.perf_counter()
        if self._last_ts is None:
            self._last_ts = now
            return
        dt = now - self._last_ts
        self._last_ts = now

        rps = self.model.rps * self._speed_mult

        if self._mode == MODE_SPIN:
            self._angle_rad += rps * 2 * math.pi * dt
            self._refresh_canvas(black=False)

        elif self._mode == MODE_FREEZE:
            # Advance angle by exactly 1/N rotation every 1/25 s tick
            self._freeze_acc += dt
            tick_interval = 1.0 / STROBE_HZ
            if self._freeze_acc >= tick_interval:
                self._freeze_acc -= tick_interval
                self._angle_rad += (2 * math.pi) / self.model.frames_needed
                self._refresh_canvas(black=False)
            # else: do nothing — frame holds still

        elif self._mode == MODE_BLINK:
            self._angle_rad += rps * 2 * math.pi * dt
            self._strobe_acc += dt
            tick_interval = 1.0 / (STROBE_HZ * 2)  # toggle at 2× rate = on/off at 25 Hz
            if self._strobe_acc >= tick_interval:
                self._strobe_acc -= tick_interval
                self._strobe_vis = not self._strobe_vis
            self._refresh_canvas(black=not self._strobe_vis)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _refresh_canvas(self, black: bool):
        qimg = self.renderer.render(
            self.model,
            self._canvas_size,
            self._angle_rad,
            background_black=black,
        )
        pixmap = QPixmap.fromImage(qimg)
        self._canvas.setPixmap(pixmap)

    # ------------------------------------------------------------------
    # Accessors for export
    # ------------------------------------------------------------------

    @property
    def current_angle(self) -> float:
        return self._angle_rad
