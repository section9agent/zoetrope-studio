"""
renderer.py
RecordRenderer — converts a RecordModel into a QImage using QPainter.
Used by both the live preview (screen DPI, ~60 fps) and PNG export (300+ DPI, one frame).
"""
from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtGui import (
    QImage, QPainter, QPen, QBrush, QColor, QFont,
    QTransform, QPainterPath,
)

from record_model import RecordModel


# ---------------------------------------------------------------------------
# Ring colour palette (matches the dark-theme widget colours)
# ---------------------------------------------------------------------------

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
    """
    Stateless renderer.  Call render() to get a QImage.
    All geometry is derived from the RecordModel at render time.
    """

    def render(
        self,
        model: RecordModel,
        size_px: int,
        angle_rad: float,
        background_black: bool = False,
    ) -> QImage:
        """
        Render the disc to a square QImage of size_px × size_px.

        Args:
            model:            The RecordModel to render.
            size_px:          Output image side length in pixels.
            angle_rad:        Current rotation angle in radians.
            background_black: If True, return a solid black image (strobe off-frame).
        """
        img = QImage(size_px, size_px, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(QColor(0, 0, 0, 255))

        if background_black:
            return img

        dpi = size_px / model.diameter_in    # pixels per inch for this render
        cx = size_px / 2.0
        cy = size_px / 2.0

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # -- Clip to disc circle --
        disc_r_px = (model.diameter_in / 2.0) * dpi
        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(cx, cy), disc_r_px, disc_r_px)
        painter.setClipPath(clip_path)

        # -- Vinyl background --
        painter.fillRect(img.rect(), QColor(17, 17, 17))

        # -- Groove guides --
        if model.show_guides:
            self._draw_grooves(painter, cx, cy, dpi, model)

        # -- Rings (rotated) --
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(angle_rad))
        self._draw_rings(painter, model, dpi)
        painter.restore()

        # -- Center label (does NOT rotate) --
        self._draw_label(painter, cx, cy, dpi, model)

        painter.end()
        return img

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _draw_grooves(self, painter: QPainter, cx: float, cy: float, dpi: float, model: RecordModel):
        """Faint concentric grooves across the playable area."""
        pen = QPen(QColor(90, 90, 90, 70))
        pen.setWidthF(0.4)
        painter.setPen(pen)
        step_in = 0.06   # groove spacing in inches
        r = model.inner_r_in
        while r <= model.outer_r_in:
            r_px = r * dpi
            painter.drawEllipse(QPointF(cx, cy), r_px, r_px)
            r += step_in

    def _draw_rings(self, painter: QPainter, model: RecordModel, dpi: float):
        """Draw all rings centred at (0,0) — caller has already translated."""
        n_slots = model.frames_needed
        ring_h_in = model.ring_height_in()

        for ring_idx, ring in enumerate(model.rings):
            outer_r_in = model.ring_outer_r_in(ring_idx)
            inner_r_in = model.ring_inner_r_in(ring_idx)
            mid_r_in   = model.ring_mid_r_in(ring_idx)
            outer_r_px = outer_r_in * dpi
            inner_r_px = inner_r_in * dpi
            mid_r_px   = mid_r_in   * dpi
            ring_h_px  = ring_h_in  * dpi

            color = RING_COLORS[ring_idx % len(RING_COLORS)]

            for slot in range(n_slots):
                frame_img = ring.frame_for_slot(slot)
                if frame_img is None:
                    continue

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
        clip_path.arcMoveTo(outer_rect, start_a)
        clip_path.arcTo(outer_rect, start_a, span_a)
        clip_path.arcTo(inner_rect, start_a + span_a, -span_a)
        clip_path.closeSubpath()

        painter.setClipPath(clip_path, Qt.ClipOperation.IntersectClip)
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

        painter.restore()

    def _draw_label(self, painter: QPainter, cx: float, cy: float, dpi: float, model: RecordModel):
        """Draw the non-rotating center label."""
        label_r_px   = model.label_r_in   * dpi
        spindle_r_px = model.spindle_r_in * dpi

        lc = model.label_color
        label_color = QColor(lc[0], lc[1], lc[2])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(label_color))
        painter.drawEllipse(QPointF(cx, cy), label_r_px, label_r_px)

        # Subtle rings on label
        for i in range(5):
            frac = 0.25 + i * 0.13
            r_px = label_r_px * frac
            painter.setPen(QPen(QColor(255, 255, 255, 10)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), r_px, r_px)

        # Spindle hole
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(QPointF(cx, cy), spindle_r_px, spindle_r_px)

        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(QPointF(cx, cy), spindle_r_px * 0.5, spindle_r_px * 0.5)
