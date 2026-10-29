"""
ring_manager_widget.py
Left panel: drop zone, ring list with reorder controls, add/remove buttons.
<<<<<<< HEAD
Each ring row shows a height spinner so the user can set ring_height_in.
=======
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
Emits ring_changed signal whenever the model's ring list changes.
"""
from __future__ import annotations
import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QColor, QIcon, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QAbstractItemView,
<<<<<<< HEAD
    QSizePolicy, QFrame, QDoubleSpinBox,
)

from record_model import RecordModel, RingModel, MIN_RING_HEIGHT_IN
=======
    QSizePolicy, QFrame,
)

from record_model import RecordModel, RingModel
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
from gif_loader import load_gif, load_static_image

RING_COLORS = [
    "#1D9E75", "#378ADD", "#EF9F27", "#D4537E",
    "#7F77DD", "#D85A30", "#97C459", "#aaaaaa",
]

SUPPORTED_EXTS = {".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}


class DropZone(QLabel):
    """A labelled drop target that also acts as an "Add Image" button."""
    file_dropped = pyqtSignal(str)   # emits a single file path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Drop image / GIF here\nor click to browse")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._normal_style = (
            "border: 2px dashed #333; border-radius: 10px; color: #666;"
            "font-size: 12px; background: #161616;"
        )
        self._hover_style = (
            "border: 2px dashed #1D9E75; border-radius: 10px; color: #1D9E75;"
            "font-size: 12px; background: #0a1e17;"
        )
        self.setStyleSheet(self._normal_style)

    # ------------------------------------------------------------------
    # Mouse click → open file dialog
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._browse()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open image or GIF",
            str(Path.home()),
            "Images (*.gif *.png *.jpg *.jpeg *.bmp *.webp *.tiff);;All files (*)",
        )
        if path:
            self.file_dropped.emit(path)

    # ------------------------------------------------------------------
    # Drag-and-drop
    # ------------------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self._hover_style)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._normal_style)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(self._normal_style)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).suffix.lower() in SUPPORTED_EXTS:
                self.file_dropped.emit(path)
                break   # one ring at a time


<<<<<<< HEAD
class RingRowWidget(QWidget):
    """Custom row widget for one ring in the list, includes a height spinner."""

    height_changed = pyqtSignal(float)   # new height_in value
=======
class RingListItem(QWidget):
    """Custom row widget for one ring in the list."""
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

    def __init__(self, ring: RingModel, ring_index: int, parent=None):
        super().__init__(parent)
        color = RING_COLORS[ring_index % len(RING_COLORS)]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Color swatch
        swatch = QLabel()
        swatch.setFixedSize(12, 12)
        swatch.setStyleSheet(
            f"background: {color}; border-radius: 6px; border: none;"
        )
        layout.addWidget(swatch)

        # Ring name + frame count
        info = QVBoxLayout()
        info.setSpacing(1)
<<<<<<< HEAD
        self._name_label = QLabel(ring.name)
        self._name_label.setStyleSheet("color: #ddd; font-size: 12px; font-weight: 600;")
        self._name_label.setMaximumWidth(120)
        frames_label = QLabel(
            f"{'GIF' if ring.is_gif() else 'image'}  ·  {ring.frame_count} fr"
        )
        frames_label.setStyleSheet("color: #666; font-size: 10px;")
        info.addWidget(self._name_label)
        info.addWidget(frames_label)
        layout.addLayout(info, stretch=1)

        # Height spinner (inches)
        h_box = QVBoxLayout()
        h_box.setSpacing(1)
        h_lbl = QLabel("h (in)")
        h_lbl.setStyleSheet("color: #555; font-size: 9px;")
        h_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spin = QDoubleSpinBox()
        self._spin.setRange(MIN_RING_HEIGHT_IN, 4.0)
        self._spin.setSingleStep(0.05)
        self._spin.setDecimals(2)
        self._spin.setValue(ring.height_in)
        self._spin.setFixedWidth(60)
        self._spin.setFixedHeight(22)
        self._spin.setStyleSheet("""
            QDoubleSpinBox {
                background: #1a1a1a; color: #ccc; border: 1px solid #2a2a2a;
                border-radius: 4px; font-size: 11px; padding: 0 2px;
            }
            QDoubleSpinBox:focus { border-color: #378ADD; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 14px; background: #222; border: none;
            }
        """)
        self._spin.valueChanged.connect(lambda v: self.height_changed.emit(v))

        h_box.addWidget(h_lbl)
        h_box.addWidget(self._spin)
        layout.addLayout(h_box)

=======
        name_label = QLabel(ring.name)
        name_label.setStyleSheet("color: #ddd; font-size: 12px; font-weight: 600;")
        name_label.setMaximumWidth(160)
        frames_label = QLabel(
            f"{'GIF' if ring.is_gif() else 'image'}  •  {ring.frame_count} frame{'s' if ring.frame_count != 1 else ''}"
        )
        frames_label.setStyleSheet("color: #666; font-size: 10px;")
        info.addWidget(name_label)
        info.addWidget(frames_label)
        layout.addLayout(info, stretch=1)

>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        # Ring position badge
        pos = QLabel(f"#{ring_index + 1}")
        pos.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: bold;"
        )
        layout.addWidget(pos)

<<<<<<< HEAD
    def ring_name(self) -> str:
        return self._name_label.text()

=======
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

class RingManagerWidget(QWidget):
    """Left panel: manages the list of rings in the RecordModel."""

    ring_changed = pyqtSignal()   # emitted whenever rings change

    def __init__(self, model: RecordModel, parent=None):
        super().__init__(parent)
        self.model = model
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Section title
        title = QLabel("Rings")
        title.setStyleSheet("color: #888; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;")
        layout.addWidget(title)

        # Drop zone / add button
        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self._drop_zone)

        # Ring list
        self._list = QListWidget()
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setStyleSheet("""
            QListWidget {
                background: #141414; border: 1px solid #252525;
                border-radius: 8px; padding: 4px;
            }
            QListWidget::item {
                border-radius: 6px; padding: 2px;
            }
            QListWidget::item:selected {
                background: #1e2e25;
            }
            QListWidget::item:hover:!selected {
                background: #1a1a1a;
            }
        """)
        self._list.setMinimumHeight(200)
        self._list.model().rowsMoved.connect(self._on_rows_moved)
        self._list.currentRowChanged.connect(self._update_controls)
        layout.addWidget(self._list, stretch=1)

        # Ring info label
        self._info_label = QLabel()
        self._info_label.setStyleSheet("color: #555; font-size: 10px;")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info_label)

        # Control buttons
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(4)

        self._btn_up = self._make_icon_btn("▲", "#378ADD", self._move_up)
        self._btn_dn = self._make_icon_btn("▼", "#378ADD", self._move_down)
        self._btn_del = self._make_icon_btn("✕", "#D4537E", self._remove_ring)
        self._btn_clear = QPushButton("Clear all")
        self._btn_clear.setFixedHeight(28)
        self._btn_clear.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888; border: 1px solid #2a2a2a;
                border-radius: 6px; font-size: 11px; padding: 0 8px;
            }
            QPushButton:hover { background: #2a1010; color: #D4537E; border-color: #3a1a1a; }
        """)
        self._btn_clear.clicked.connect(self._clear_all)

        ctrl_row.addWidget(self._btn_up)
        ctrl_row.addWidget(self._btn_dn)
        ctrl_row.addWidget(self._btn_del)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self._btn_clear)
        layout.addLayout(ctrl_row)

        self._rebuild_list()

    def _make_icon_btn(self, text: str, color: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(28, 28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e1e1e; color: #888; border: 1px solid #2a2a2a;
                border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #252525; color: {color}; border-color: #333; }}
            QPushButton:disabled {{ color: #333; border-color: #1e1e1e; }}
        """)
        btn.clicked.connect(slot)
        return btn

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_model(self, model: RecordModel):
        self.model = model
        self._rebuild_list()

    # ------------------------------------------------------------------
    # File loading
    # ------------------------------------------------------------------

    def _on_file_dropped(self, path: str):
        ext = Path(path).suffix.lower()
        name = Path(path).stem[:30]

        full, remaining = self.model.is_full()
        if full:
            QMessageBox.warning(
                self, "Disc Full",
                f"No room for another ring.\n\n"
                f"Current rings: {len(self.model.rings)}\n"
                f"Remaining radial space: {remaining:.3f}\""
            )
            return

        if ext == ".gif":
            frames = load_gif(path)
        else:
            frames = load_static_image(path)

        if not frames:
            QMessageBox.warning(self, "Load Error", f"Could not load:\n{path}")
            return

<<<<<<< HEAD
        ring = RingModel(name, frames, height_in=self.model.default_ring_height_in)
=======
        ring = RingModel(name, frames)
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        self.model.add_ring(ring)
        self._rebuild_list()
        self.ring_changed.emit()

        # Pre-emptive warning if now full after adding
        full, remaining = self.model.is_full()
        if full:
            QMessageBox.information(
                self, "Disc Full",
                f"The disc is now full ({len(self.model.rings)} rings).\n"
                f"Remaining radial space: {remaining:.3f}\""
            )

    # ------------------------------------------------------------------
    # Ring list management
    # ------------------------------------------------------------------

    def _rebuild_list(self):
        self._list.blockSignals(True)
        sel_row = self._list.currentRow()
        self._list.clear()
        for idx, ring in enumerate(self.model.rings):
            item = QListWidgetItem(self._list)
<<<<<<< HEAD
            row_widget = RingRowWidget(ring, idx)
            # Connect height spinner → update ring model → redraw
            ring_ref = ring
            row_widget.height_changed.connect(
                lambda v, r=ring_ref: self._on_ring_height_changed(r, v)
            )
=======
            row_widget = RingListItem(ring, idx)
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
            item.setSizeHint(row_widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, row_widget)
        # Restore selection
        if 0 <= sel_row < len(self.model.rings):
            self._list.setCurrentRow(sel_row)
        self._list.blockSignals(False)
        self._update_controls()
        self._update_info_label()

<<<<<<< HEAD
    def _on_ring_height_changed(self, ring: RingModel, new_height: float):
        ring.height_in = max(MIN_RING_HEIGHT_IN, new_height)
        self._update_info_label()
        self.ring_changed.emit()

    def _on_rows_moved(self, parent, start, end, dest, row):
        """Sync drag-reorder in the list widget back to the model."""
=======
    def _on_rows_moved(self, parent, start, end, dest, row):
        """Sync drag-reorder in the list widget back to the model."""
        # Rebuild model.rings from the current list widget order
        # The list widget already has the new order after the move.
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        old_rings = list(self.model.rings)
        new_rings = []
        for i in range(self._list.count()):
            widget = self._list.itemWidget(self._list.item(i))
<<<<<<< HEAD
            ring_name = widget.ring_name()
=======
            # The widget was created with a ring_index; we need to find the ring
            # We'll use the name label text to match (fragile but sufficient)
            name_label = widget.layout().itemAt(1).layout().itemAt(0).widget()
            ring_name = name_label.text()
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
            for r in old_rings:
                if r.name == ring_name:
                    new_rings.append(r)
                    break
        if len(new_rings) == len(self.model.rings):
            self.model.rings = new_rings
        self._rebuild_list()
        self.ring_changed.emit()

    def _move_up(self):
        row = self._list.currentRow()
        if row > 0:
            self.model.move_ring(row, -1)
            self._rebuild_list()
            self._list.setCurrentRow(row - 1)
            self.ring_changed.emit()

    def _move_down(self):
        row = self._list.currentRow()
        if row < len(self.model.rings) - 1:
            self.model.move_ring(row, 1)
            self._rebuild_list()
            self._list.setCurrentRow(row + 1)
            self.ring_changed.emit()

    def _remove_ring(self):
        row = self._list.currentRow()
        if 0 <= row < len(self.model.rings):
            self.model.remove_ring(row)
            self._rebuild_list()
            self.ring_changed.emit()

    def _clear_all(self):
        if not self.model.rings:
            return
        reply = QMessageBox.question(
            self, "Clear All Rings",
            "Remove all rings from the disc?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.clear_rings()
            self._rebuild_list()
            self.ring_changed.emit()

    def _update_controls(self):
        n = len(self.model.rings)
        row = self._list.currentRow()
        self._btn_up.setEnabled(row > 0)
        self._btn_dn.setEnabled(0 <= row < n - 1)
        self._btn_del.setEnabled(row >= 0 and n > 0)
        self._btn_clear.setEnabled(n > 0)

    def _update_info_label(self):
        n = len(self.model.rings)
<<<<<<< HEAD
        available = self.model.available_radial_in
        remaining = self.model.remaining_radial_in()
        if n == 0:
            self._info_label.setText(f"Available: {available:.2f}\"  ·  No rings yet")
        else:
            used = self.model.used_radial_in()
            self._info_label.setText(
                f"{n} ring{'s' if n != 1 else ''}  ·  {used:.2f}\" used  ·  {remaining:.2f}\" free"
=======
        h = self.model.ring_height_in()
        available = self.model.available_radial_in
        if n == 0:
            self._info_label.setText(f"Available: {available:.2f}\"  ·  No rings yet")
        else:
            self._info_label.setText(
                f"{n} ring{'s' if n != 1 else ''}  ·  each {h:.3f}\" tall  ·  {available:.2f}\" playable"
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
            )
