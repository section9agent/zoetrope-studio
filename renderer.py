"""
renderer.py
RecordRenderer — converts a RecordModel into a QImage using QPainter.
<<<<<<< HEAD
Used by both the live preview (~60 fps) and PNG export (300+ DPI, one frame).

Image drawing rules:
  - Scale the image so its HEIGHT fills the ring height exactly (no vertical stretch).
  - Maintain aspect ratio — width scales proportionally.
  - If the scaled image is wider than the arc slot, crop it centrally (no horizontal squeeze).
  - No gaps between rings.
"""
from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QRectF, QPointF, QRect
from PyQt6.QtGui import (
    QImage, QPainter, QPen, QBrush, QColor, QFont,
    QPainterPath,
=======
Used by both the live preview (screen DPI, ~60 fps) and PNG export (300+ DPI, one frame).
"""
from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtGui import (
    QImage, QPainter, QPen, QBrush, QColor, QFont,
    QTransform, QPainterPath,
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
)

from record_model import RecordModel


<<<<<<< HEAD
=======
# ---------------------------------------------------------------------------
# Ring colour palette (matches the dark-theme widget colours)
# ---------------------------------------------------------------------------

>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
RING_COLORS = [
    QColor("#1D9E75"),
    QColor("#378ADD"),
    QColor("#EF9F27"),
    QColor("#D4537E"),
    QColor("#7F77DD"),
    QColor("#D85A30"),
    QColor("#97C459"),
    QColor("#aaaaaa"),
]


class RecordRenderer:
<<<<<<< HEAD
    """Stateless renderer. Call render() to get a QImage."""
=======
    """
    Stateless renderer.  Call render() to get a QImage.
    All geometry is derived from the RecordModel at render time.
    """
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

    def render(
        self,
        model: RecordModel,
        size_px: int,
        angle_rad: float,
        background_black: bool = False,
    ) -> QImage:
<<<<<<< HEAD
=======
        """
        Render the disc to a square QImage of size_px × size_px.

        Args:
            model:            The RecordModel to render.
            size_px:          Output image side length in pixels.
            angle_rad:        Current rotation angle in radians.
            background_black: If True, return a solid black image (strobe off-frame).
        """
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        img = QImage(size_px, size_px, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(QColor(0, 0, 0, 255))

        if background_black:
            return img

<<<<<<< HEAD
        dpi = size_px / model.diameter_in
        cx  = size_px / 2.0
        cy  = size_px / 2.0
=======
        dpi = size_px / model.diameter_in    # pixels per inch for this render
        cx = size_px / 2.0
        cy = size_px / 2.0
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

<<<<<<< HEAD
        # Clip everything to the disc circle
=======
        # -- Clip to disc circle --
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        disc_r_px = (model.diameter_in / 2.0) * dpi
        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(cx, cy), disc_r_px, disc_r_px)
        painter.setClipPath(clip_path)

<<<<<<< HEAD
        # Vinyl background
        painter.fillRect(img.rect(), QColor(17, 17, 17))

        # Groove guides
        if model.show_guides:
            self._draw_grooves(painter, cx, cy, dpi, model)

        # Rings (rotated together)
=======
        # -- Vinyl background --
        painter.fillRect(img.rect(), QColor(17, 17, 17))

        # -- Groove guides --
        if model.show_guides:
            self._draw_grooves(painter, cx, cy, dpi, model)

        # -- Rings (rotated) --
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(angle_rad))
        self._draw_rings(painter, model, dpi)
        painter.restore()

<<<<<<< HEAD
        # Center label (does NOT rotate)
=======
        # -- Center label (does NOT rotate) --
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        self._draw_label(painter, cx, cy, dpi, model)

        painter.end()
        return img

    # ------------------------------------------------------------------
<<<<<<< HEAD

    def _draw_grooves(self, painter, cx, cy, dpi, model):
        pen = QPen(QColor(90, 90, 90, 70))
        pen.setWidthF(0.4)
        painter.setPen(pen)
        step_in = 0.06
=======
    # Private helpers
    # ------------------------------------------------------------------

    def _draw_grooves(self, painter: QPainter, cx: float, cy: float, dpi: float, model: RecordModel):
        """Faint concentric grooves across the playable area."""
        pen = QPen(QColor(90, 90, 90, 70))
        pen.setWidthF(0.4)
        painter.setPen(pen)
        step_in = 0.06   # groove spacing in inches
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        r = model.inner_r_in
        while r <= model.outer_r_in:
            r_px = r * dpi
            painter.drawEllipse(QPointF(cx, cy), r_px, r_px)
            r += step_in

<<<<<<< HEAD
    def _draw_rings(self, painter, model: RecordModel, dpi: float):
        n_slots = model.frames_needed
=======
    def _draw_rings(self, painter: QPainter, model: RecordModel, dpi: float):
        """Draw all rings centred at (0,0) — caller has already translated."""
        n_slots = model.frames_needed
        ring_h_in = model.ring_height_in()
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

        for ring_idx, ring in enumerate(model.rings):
            outer_r_in = model.ring_outer_r_in(ring_idx)
            inner_r_in = model.ring_inner_r_in(ring_idx)
            mid_r_in   = model.ring_mid_r_in(ring_idx)
<<<<<<< HEAD
            ring_h_in  = ring.height_in

=======
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
            outer_r_px = outer_r_in * dpi
            inner_r_px = inner_r_in * dpi
            mid_r_px   = mid_r_in   * dpi
            ring_h_px  = ring_h_in  * dpi

            color = RING_COLORS[ring_idx % len(RING_COLORS)]

            for slot in range(n_slots):
                frame_img = ring.frame_for_slot(slot)
                if frame_img is None:
                    continue
<<<<<<< HEAD
                slot_angle = (slot / n_slots) * 2 * math.pi - math.pi / 2.0
                self._draw_frame_slot(
                    painter, frame_img, slot_angle,
                    mid_r_px, ring_h_px, outer_r_px, inner_r_px, n_slots, dpi,
                    color, slot if model.show_frame_numbers else None,
=======

                angle_rad = (slot / n_slots) * 2 * math.pi - math.pi / 2.0
                self._draw_frame_slot(
                    painter,
                    frame_img,
                    angle_rad,
                    mid_r_px,
                    ring_h_px,
                    outer_r_px,
                    inner_r_px,
                    n_slots,
                    dpi,
                    color,
                    slot if model.show_frame_numbers else None,
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
                )

    def _draw_frame_slot(
        self,
        painter: QPainter,
        frame_img: QImage,
        angle_rad: float,
        mid_r_px: float,
        ring_h_px: float,
        outer_r_px: float,
        inner_r_px: float,
        n_slots: int,
        dpi: float,
        ring_color: QColor,
        frame_number,
    ):
<<<<<<< HEAD
        painter.save()
        painter.rotate(math.degrees(angle_rad))

        # Angular width of this slot + tiny overlap to avoid hairline gaps
        half_angle_deg = (360.0 / n_slots) / 2.0 + 0.3

        # Arc chord width at the midline radius
        arc_w_px = 2.0 * math.pi * mid_r_px / n_slots

        # ── Scale image so its HEIGHT fills ring_h_px exactly ──────────
        # Aspect ratio is preserved — width scales with height.
        # If the resulting width is wider than the arc slot, we crop centrally.
        img_w = frame_img.width()
        img_h = frame_img.height()

        if img_w > 0 and img_h > 0:
            scale    = ring_h_px / img_h          # scale to fill ring height
            scaled_w = img_w * scale
            scaled_h = ring_h_px                  # exact fill

            # Scale the source image once
            scaled_img = frame_img.scaled(
                max(1, int(scaled_w)),
                max(1, int(scaled_h)),
                Qt.AspectRatioMode.IgnoreAspectRatio,   # we computed exact dims
                Qt.TransformationMode.SmoothTransformation,
            )

            # If scaled_w > arc_w_px, crop: take the central arc_w_px columns
            draw_w = min(scaled_w, arc_w_px)
            src_x  = max(0, int((scaled_w - draw_w) / 2.0))
            src_rect = QRect(src_x, 0, int(draw_w), int(scaled_h))

            # Destination: centred horizontally on the slot axis, top at outer edge
            dest_rect = QRectF(-draw_w / 2.0, -outer_r_px, draw_w, scaled_h)
        else:
            scaled_img = frame_img
            src_rect   = frame_img.rect()
            dest_rect  = QRectF(-arc_w_px / 2.0, -outer_r_px, arc_w_px, ring_h_px)

        # ── Clip wedge ─────────────────────────────────────────────────
        clip_path  = QPainterPath()
        outer_rect = QRectF(-outer_r_px, -outer_r_px, 2 * outer_r_px, 2 * outer_r_px)
        inner_rect = QRectF(-inner_r_px, -inner_r_px, 2 * inner_r_px, 2 * inner_r_px)
        start_a    = 90.0 - half_angle_deg
        span_a     = half_angle_deg * 2.0
=======
        """Draw one frame image as a curved arc slice."""
        painter.save()
        painter.rotate(math.degrees(angle_rad))

        # Each slot occupies (360 / n_slots) degrees; we use half that as the wedge
        # half-angle, with a tiny 0.3° overlap so there are no hairline gaps.
        half_angle_deg = (360.0 / n_slots) / 2.0 + 0.3

        # Arc width at the midline radius
        arc_w_px = 2.0 * math.pi * mid_r_px / n_slots

        # Draw the image at its NATURAL size, centred in the ring slot.
        # We scale only if the image is wider than the slot arc width
        # (so it still fits), but we never stretch it taller than it is.
        img_w = frame_img.width()
        img_h = frame_img.height()

        # Scale down to fit the arc width if necessary (never scale up)
        scale = min(1.0, arc_w_px / img_w) if img_w > 0 else 1.0
        draw_w = img_w * scale
        draw_h = img_h * scale

        # Clamp draw height to the ring height (crop, don't squash)
        draw_h = min(draw_h, ring_h_px)

        # Centre horizontally on the slot, centre vertically in the ring
        draw_x = -draw_w / 2.0
        draw_y = -outer_r_px + (ring_h_px - draw_h) / 2.0
        rect = QRectF(draw_x, draw_y, draw_w, draw_h)

        # Build a clip wedge: outer arc → radial line → inner arc → radial line
        clip_path = QPainterPath()
        outer_rect = QRectF(-outer_r_px, -outer_r_px, 2 * outer_r_px, 2 * outer_r_px)
        inner_rect = QRectF(-inner_r_px, -inner_r_px, 2 * inner_r_px, 2 * inner_r_px)
        start_a = 90.0 - half_angle_deg
        span_a  = half_angle_deg * 2.0
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        clip_path.arcMoveTo(outer_rect, start_a)
        clip_path.arcTo(outer_rect, start_a, span_a)
        clip_path.arcTo(inner_rect, start_a + span_a, -span_a)
        clip_path.closeSubpath()

        painter.setClipPath(clip_path, Qt.ClipOperation.IntersectClip)
<<<<<<< HEAD
        painter.drawImage(dest_rect, scaled_img, QRectF(src_rect))

        if frame_number is not None and arc_w_px > 16:
            painter.setPen(QPen(QColor(255, 255, 255, 160)))
            font = QFont()
            font.setPixelSize(max(8, int(arc_w_px * 0.18)))
            painter.setFont(font)
            painter.drawText(dest_rect, Qt.AlignmentFlag.AlignCenter, str(frame_number + 1))
=======
        # drawImage(QRectF, QImage) still scales — use the overload that doesn't
        painter.drawImage(rect.topLeft(), frame_img.scaled(
            int(draw_w), int(draw_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

        if frame_number is not None and arc_w_px > 16:
            pen = QPen(QColor(255, 255, 255, 160))
            painter.setPen(pen)
            font = QFont()
            font.setPixelSize(max(8, int(arc_w_px * 0.18)))
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(frame_number + 1))
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

        painter.restore()

    def _draw_label(self, painter: QPainter, cx: float, cy: float, dpi: float, model: RecordModel):
<<<<<<< HEAD
        label_r_px   = model.label_r_in   * dpi
        spindle_r_px = model.spindle_r_in * dpi

        r, g, b = model.label_color
        label_color = QColor(r, g, b)
=======
        """Draw the non-rotating center label."""
        label_r_px   = model.label_r_in   * dpi
        spindle_r_px = model.spindle_r_in * dpi

        lc = model.label_color
        label_color = QColor(lc[0], lc[1], lc[2])
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(label_color))
        painter.drawEllipse(QPointF(cx, cy), label_r_px, label_r_px)

<<<<<<< HEAD
        # Custom label image (fills the label circle)
        if model.label_image is not None:
            painter.save()
            lbl_path = QPainterPath()
            lbl_path.addEllipse(QPointF(cx, cy), label_r_px, label_r_px)
            painter.setClipPath(lbl_path, Qt.ClipOperation.IntersectClip)
            d = label_r_px * 2
            painter.drawImage(
                QRectF(cx - label_r_px, cy - label_r_px, d, d),
                model.label_image,
            )
            painter.restore()
        else:
            # Subtle decorative rings
            for i in range(5):
                frac = 0.25 + i * 0.13
                r_px = label_r_px * frac
                painter.setPen(QPen(QColor(255, 255, 255, 10)))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(cx, cy), r_px, r_px)
=======
        # Subtle rings on label
        for i in range(5):
            frac = 0.25 + i * 0.13
            r_px = label_r_px * frac
            painter.setPen(QPen(QColor(255, 255, 255, 10)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), r_px, r_px)
>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6

        # Spindle hole
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(QPointF(cx, cy), spindle_r_px, spindle_r_px)
<<<<<<< HEAD
=======

>>>>>>> 620a9a6936cb87498c2d3d166f750422a99059c6
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(QPointF(cx, cy), spindle_r_px * 0.5, spindle_r_px * 0.5)
