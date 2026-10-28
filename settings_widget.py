"""
settings_widget.py
Right panel: record type toggle, visual options, label color picker, export.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCheckBox, QComboBox, QColorDialog, QFileDialog, QMessageBox,
    QFrame, QSpinBox, QSizePolicy,
)

from record_model import RecordModel, RECORD_PRESETS
from renderer import RecordRenderer


class SettingsWidget(QWidget):
    """Right panel — record settings and export controls."""

    setting_changed = pyqtSignal()   # emitted whenever any display setting changes
    model_changed   = pyqtSignal()   # emitted when record type changes (ring count changes)

    def __init__(self, model: RecordModel, parent=None):
        super().__init__(parent)
        self.model = model
        self._renderer = RecordRenderer()
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # ── Record type ──────────────────────────────────────────────
        layout.addWidget(self._section_label("Record Type"))

        type_row = QHBoxLayout()
        type_row.setSpacing(6)
        self._btn_12in = self._make_toggle_btn('12" — 33⅓', "12in", "#1D9E75")
        self._btn_7in  = self._make_toggle_btn('7" — 45',   "7in",  "#EF9F27")
        type_row.addWidget(self._btn_12in)
        type_row.addWidget(self._btn_7in)
        layout.addLayout(type_row)

        self._frames_label = QLabel()
        self._frames_label.setStyleSheet("color: #555; font-size: 10px;")
        self._frames_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._frames_label)

        # ── Visual options ────────────────────────────────────────────
        layout.addWidget(self._section_label("Display"))

        self._chk_guides = QCheckBox("Show groove guides")
        self._chk_guides.setChecked(self.model.show_guides)
        self._chk_guides.toggled.connect(self._on_guides_toggled)
        self._chk_guides.setStyleSheet("color: #ccc; font-size: 12px;")
        layout.addWidget(self._chk_guides)

        self._chk_numbers = QCheckBox("Show frame numbers")
        self._chk_numbers.setChecked(self.model.show_frame_numbers)
        self._chk_numbers.toggled.connect(self._on_numbers_toggled)
        self._chk_numbers.setStyleSheet("color: #ccc; font-size: 12px;")
        layout.addWidget(self._chk_numbers)

        # ── Label color ───────────────────────────────────────────────
        layout.addWidget(self._section_label("Label Color"))

        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        self._color_swatch = QLabel()
        self._color_swatch.setFixedSize(32, 32)
        self._color_swatch.setStyleSheet("border-radius: 6px; border: 1px solid #333;")
        self._update_color_swatch()
        color_row.addWidget(self._color_swatch)

        self._btn_color = QPushButton("Choose…")
        self._btn_color.setFixedHeight(32)
        self._btn_color.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #ccc; border: 1px solid #333;
                border-radius: 6px; font-size: 12px; padding: 0 10px;
            }
            QPushButton:hover { background: #252525; border-color: #444; color: #fff; }
        """)
        self._btn_color.clicked.connect(self._on_pick_color)
        color_row.addWidget(self._btn_color, stretch=1)
        layout.addLayout(color_row)

        # ── Spacer ────────────────────────────────────────────────────
        layout.addStretch()

        # ── Export ───────────────────────────────────────────────────
        layout.addWidget(self._section_label("Export"))

        dpi_row = QHBoxLayout()
        dpi_row.setSpacing(8)
        dpi_lbl = QLabel("DPI")
        dpi_lbl.setStyleSheet("color: #888; font-size: 12px;")
        dpi_row.addWidget(dpi_lbl)

        self._dpi_combo = QComboBox()
        self._dpi_combo.addItems(["150", "300", "600"])
        self._dpi_combo.setCurrentText("300")
        self._dpi_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e1e; color: #ccc; border: 1px solid #333;
                border-radius: 6px; font-size: 12px; padding: 4px 8px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1e1e1e; color: #ccc; selection-background-color: #252525;
                border: 1px solid #333;
            }
        """)
        dpi_row.addWidget(self._dpi_combo, stretch=1)
        layout.addLayout(dpi_row)

        self._export_size_label = QLabel()
        self._export_size_label.setStyleSheet("color: #555; font-size: 10px;")
        self._export_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._export_size_label)

        self._btn_export = QPushButton("⬇  Export PNG")
        self._btn_export.setFixedHeight(40)
        self._btn_export.setStyleSheet("""
            QPushButton {
                background: #1D9E75; color: #fff; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background: #22b886; }
            QPushButton:pressed { background: #178a62; }
            QPushButton:disabled { background: #1e1e1e; color: #444; }
        """)
        self._btn_export.clicked.connect(self._on_export)
        layout.addWidget(self._btn_export)

        # init labels
        self._update_type_buttons()
        self._update_frames_label()
        self._update_export_size_label()
        self._dpi_combo.currentTextChanged.connect(self._update_export_size_label)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            "color: #555; font-size: 10px; font-weight: 700; letter-spacing: 1px;"
        )
        return lbl

    def _make_toggle_btn(self, text: str, record_type: str, color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedHeight(34)
        btn.setProperty("record_type", record_type)
        btn.setProperty("color", color)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e1e1e; color: #888; border: 1px solid #2a2a2a;
                border-radius: 8px; font-size: 12px; font-weight: 500;
            }}
            QPushButton:checked {{
                background: {color}; color: #fff; border-color: {color};
            }}
            QPushButton:hover:!checked {{
                background: #242424; color: #ccc; border-color: #333;
            }}
        """)
        btn.clicked.connect(lambda _, rt=record_type: self._on_record_type(rt))
        return btn

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_model(self, model: RecordModel):
        self.model = model
        self._update_type_buttons()
        self._update_frames_label()
        self._update_export_size_label()
        self._update_color_swatch()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_record_type(self, rt: str):
        if self.model.record_type == rt:
            self._update_type_buttons()
            return
        self.model.record_type = rt
        self.model.clear_rings()
        self._update_type_buttons()
        self._update_frames_label()
        self._update_export_size_label()
        self.model_changed.emit()
        self.setting_changed.emit()

    def _on_guides_toggled(self, checked: bool):
        self.model.show_guides = checked
        self.setting_changed.emit()

    def _on_numbers_toggled(self, checked: bool):
        self.model.show_frame_numbers = checked
        self.setting_changed.emit()

    def _on_pick_color(self):
        r, g, b = self.model.label_color
        initial = QColor(r, g, b)
        color = QColorDialog.getColor(initial, self, "Label Color")
        if color.isValid():
            self.model.label_color = (color.red(), color.green(), color.blue())
            self._update_color_swatch()
            self.setting_changed.emit()

    def _on_export(self):
        if not self.model.rings:
            QMessageBox.information(self, "Nothing to export", "Add at least one ring before exporting.")
            return

        dpi = int(self._dpi_combo.currentText())
        size_px = round(self.model.diameter_in * dpi)

        path, _ = QFileDialog.getSaveFileName(
            self, "Export PNG",
            f"zoetrope_{self.model.record_type}_{dpi}dpi.png",
            "PNG Images (*.png)",
        )
        if not path:
            return

        import math
        qimg = self._renderer.render(self.model, size_px, 0.0, background_black=False)
        if qimg.save(path, "PNG"):
            QMessageBox.information(
                self, "Export complete",
                f"Saved {size_px}×{size_px} px PNG\n{path}"
            )
        else:
            QMessageBox.critical(self, "Export failed", f"Could not write to:\n{path}")

    # ------------------------------------------------------------------
    # UI updates
    # ------------------------------------------------------------------

    def _update_type_buttons(self):
        rt = self.model.record_type
        self._btn_12in.setChecked(rt == "12in")
        self._btn_7in.setChecked(rt == "7in")

    def _update_frames_label(self):
        n = self.model.frames_needed
        rpm = self.model.rpm
        self._frames_label.setText(
            f"{rpm:.4g} RPM  ·  {n} frames/ring  ·  {self.model.available_radial_in:.2f}\" playable"
        )

    def _update_export_size_label(self):
        dpi = int(self._dpi_combo.currentText())
        size_px = round(self.model.diameter_in * dpi)
        self._export_size_label.setText(f"{size_px} × {size_px} px at {dpi} DPI")

    def _update_color_swatch(self):
        r, g, b = self.model.label_color
        self._color_swatch.setStyleSheet(
            f"background: rgb({r},{g},{b}); border-radius: 6px; border: 1px solid #333;"
        )
