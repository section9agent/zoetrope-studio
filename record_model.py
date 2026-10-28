"""
record_model.py
Pure data model — no Qt imports, no UI logic.
All geometry is computed in inches then converted to pixels on demand.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math


# ---------------------------------------------------------------------------
# Record presets
# ---------------------------------------------------------------------------

RECORD_PRESETS = {
    "12in": {
        "label": '12" — 33⅓ RPM',
        "diameter_in": 12.0,
        "rpm": 100.0 / 3.0,          # 33.333…
        "outer_r_in": 5.75,           # playable area outer radius
        "inner_r_in": 1.75,           # label edge (inner playable radius)
        "label_r_in": 1.75,           # center label radius (same as inner)
        "spindle_r_in": 0.075,        # ~3/32" spindle hole
    },
    "7in": {
        "label": '7" — 45 RPM',
        "diameter_in": 7.0,
        "rpm": 45.0,
        "outer_r_in": 3.25,
        "inner_r_in": 0.75,
        "label_r_in": 0.75,
        "spindle_r_in": 0.125,        # 45s have a wider spindle (1/4")
    },
}

TARGET_FPS = 25          # strobe / persistence-of-vision frame rate
MIN_RING_HEIGHT_IN = 0.08  # minimum useful ring height in inches (~24px at 300dpi)


# ---------------------------------------------------------------------------
# RingModel
# ---------------------------------------------------------------------------

class RingModel:
    """One animation ring on the disc.  frames is a list of QImage (loaded externally)."""

    def __init__(self, name: str, frames: list):
        self.name = name
        self.frames: list = frames   # list[QImage]

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def frame_for_slot(self, slot_index: int):
        """Return the QImage for this slot (wraps if fewer frames than slots)."""
        if not self.frames:
            return None
        return self.frames[slot_index % len(self.frames)]

    def is_gif(self) -> bool:
        return self.frame_count > 1


# ---------------------------------------------------------------------------
# RecordModel
# ---------------------------------------------------------------------------

class RecordModel:
    """
    Central data model.  Holds record type and all rings.
    All geometry accessors accept an optional dpi argument; pixel values are
    returned when dpi is given, inch values otherwise.
    """

    def __init__(self, record_type: str = "12in"):
        self._record_type = record_type
        self.rings: List[RingModel] = []
        # UI settings (not geometry)
        self.show_guides: bool = True
        self.show_frame_numbers: bool = False
        self.label_color: Tuple[int, int, int] = (26, 26, 46)  # dark blue-black
        self.ring_gap_in: float = 0.02   # gap between rings in inches

    # ------------------------------------------------------------------
    # Record type
    # ------------------------------------------------------------------

    @property
    def record_type(self) -> str:
        return self._record_type

    @record_type.setter
    def record_type(self, value: str):
        if value not in RECORD_PRESETS:
            raise ValueError(f"Unknown record type: {value}")
        self._record_type = value

    @property
    def preset(self) -> dict:
        return RECORD_PRESETS[self._record_type]

    @property
    def diameter_in(self) -> float:
        return self.preset["diameter_in"]

    @property
    def rpm(self) -> float:
        return self.preset["rpm"]

    @property
    def rps(self) -> float:
        return self.rpm / 60.0

    @property
    def frames_needed(self) -> int:
        """Number of frame slots per ring for persistence-of-vision at TARGET_FPS."""
        return round(TARGET_FPS / self.rps)

    @property
    def outer_r_in(self) -> float:
        return self.preset["outer_r_in"]

    @property
    def inner_r_in(self) -> float:
        return self.preset["inner_r_in"]

    @property
    def label_r_in(self) -> float:
        return self.preset["label_r_in"]

    @property
    def spindle_r_in(self) -> float:
        return self.preset["spindle_r_in"]

    @property
    def available_radial_in(self) -> float:
        """Total playable radial space in inches."""
        return self.outer_r_in - self.inner_r_in

    # ------------------------------------------------------------------
    # Ring geometry
    # ------------------------------------------------------------------

    def ring_height_in(self) -> float:
        """Height of each ring in inches (equal division, minus gaps)."""
        n = len(self.rings)
        if n == 0:
            return self.available_radial_in
        total_gap = self.ring_gap_in * (n - 1)
        return max(0.0, (self.available_radial_in - total_gap) / n)

    def ring_height_px(self, dpi: float) -> float:
        return self.ring_height_in() * dpi

    def ring_outer_r_in(self, ring_index: int) -> float:
        """Outer radius of ring at ring_index (ring 0 = outermost)."""
        h = self.ring_height_in()
        return self.outer_r_in - ring_index * (h + self.ring_gap_in)

    def ring_inner_r_in(self, ring_index: int) -> float:
        return self.ring_outer_r_in(ring_index) - self.ring_height_in()

    def ring_mid_r_in(self, ring_index: int) -> float:
        return (self.ring_outer_r_in(ring_index) + self.ring_inner_r_in(ring_index)) / 2.0

    # ------------------------------------------------------------------
    # Fullness check
    # ------------------------------------------------------------------

    def remaining_radial_in(self) -> float:
        """How many inches remain if we were to add one more ring."""
        n = len(self.rings) + 1   # hypothetical new count
        total_gap = self.ring_gap_in * (n - 1)
        new_h = (self.available_radial_in - total_gap) / n
        return new_h

    def is_full(self) -> Tuple[bool, float]:
        """
        Returns (is_full: bool, remaining_height_in: float).
        is_full is True when adding another ring would shrink each ring
        below MIN_RING_HEIGHT_IN.
        """
        remaining = self.remaining_radial_in()
        return remaining < MIN_RING_HEIGHT_IN, remaining

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------

    def add_ring(self, ring: RingModel) -> bool:
        """Add a ring.  Returns False (and does NOT add) if disc is full."""
        full, _ = self.is_full()
        if full:
            return False
        self.rings.append(ring)
        return True

    def remove_ring(self, index: int):
        if 0 <= index < len(self.rings):
            self.rings.pop(index)

    def move_ring(self, index: int, direction: int):
        """Move ring at index up (-1) or down (+1)."""
        j = index + direction
        if 0 <= j < len(self.rings):
            self.rings[index], self.rings[j] = self.rings[j], self.rings[index]

    def clear_rings(self):
        self.rings.clear()
