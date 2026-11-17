"""
record_model.py
Pure data model — no Qt imports, no UI logic.
All geometry is computed in inches then converted to pixels on demand.

Ring geometry change: each ring now has its OWN height_in.
Rings stack from the outer edge inward with NO gap between them.
The disc is "full" when the next ring would go below the inner label edge.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import math


# ---------------------------------------------------------------------------
# Record presets
# ---------------------------------------------------------------------------

RECORD_PRESETS = {
    "12in": {
        "label": '12" — 33⅓ RPM',
        "diameter_in": 12.0,
        "rpm": 100.0 / 3.0,
        "outer_r_in": 5.75,
        "inner_r_in": 1.75,
        "label_r_in": 1.75,
        "spindle_r_in": 0.075,
        "default_ring_height_in": 0.5,   # sensible starting height for a new ring
    },
    "7in": {
        "label": '7" — 45 RPM',
        "diameter_in": 7.0,
        "rpm": 45.0,
        "outer_r_in": 3.25,
        "inner_r_in": 0.75,
        "label_r_in": 0.75,
        "spindle_r_in": 0.125,
        "default_ring_height_in": 0.35,
    },
}

TARGET_FPS = 25
MIN_RING_HEIGHT_IN = 0.08   # smallest a ring is allowed to be


# ---------------------------------------------------------------------------
# RingModel
# ---------------------------------------------------------------------------

class RingModel:
    """One animation ring on the disc."""

    def __init__(self, name: str, frames: list, height_in: float = 0.5):
        self.name   = name
        self.frames: list = frames      # list[QImage]
        self.height_in: float = max(MIN_RING_HEIGHT_IN, height_in)

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def frame_for_slot(self, slot_index: int):
        if not self.frames:
            return None
        return self.frames[slot_index % len(self.frames)]

    def is_gif(self) -> bool:
        return self.frame_count > 1


# ---------------------------------------------------------------------------
# RecordModel
# ---------------------------------------------------------------------------

class RecordModel:
    def __init__(self, record_type: str = "12in"):
        self._record_type = record_type
        self.rings: List[RingModel] = []
        self.show_guides: bool       = True
        self.show_frame_numbers: bool = False
        self.label_color: Tuple[int, int, int] = (26, 26, 46)
        self.label_image = None   # QImage or None — custom center label photo

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
    def default_ring_height_in(self) -> float:
        return self.preset["default_ring_height_in"]

    @property
    def available_radial_in(self) -> float:
        return self.outer_r_in - self.inner_r_in

    # ------------------------------------------------------------------
    # Ring geometry — each ring has its own height, stacked, no gaps
    # ------------------------------------------------------------------

    def ring_outer_r_in(self, ring_index: int) -> float:
        """Outer radius of ring[ring_index]. Ring 0 is the outermost."""
        r = self.outer_r_in
        for i in range(ring_index):
            r -= self.rings[i].height_in
        return r

    def ring_inner_r_in(self, ring_index: int) -> float:
        return self.ring_outer_r_in(ring_index) - self.rings[ring_index].height_in

    def ring_mid_r_in(self, ring_index: int) -> float:
        return (self.ring_outer_r_in(ring_index) + self.ring_inner_r_in(ring_index)) / 2.0

    # ------------------------------------------------------------------
    # Fullness / space
    # ------------------------------------------------------------------

    def used_radial_in(self) -> float:
        return sum(r.height_in for r in self.rings)

    def remaining_radial_in(self) -> float:
        return max(0.0, self.available_radial_in - self.used_radial_in())

    def is_full(self) -> Tuple[bool, float]:
        """Returns (would_be_full_after_adding_default_ring, remaining_inches)."""
        remaining = self.remaining_radial_in()
        return remaining < MIN_RING_HEIGHT_IN, remaining

    def can_fit_height(self, height_in: float) -> bool:
        return self.remaining_radial_in() >= height_in

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------

    def add_ring(self, ring: RingModel) -> bool:
        """Add ring if it fits. Returns False if there's not enough space."""
        if not self.can_fit_height(ring.height_in):
            # Try to squeeze it to whatever remains
            remaining = self.remaining_radial_in()
            if remaining < MIN_RING_HEIGHT_IN:
                return False
            ring.height_in = remaining
        self.rings.append(ring)
        return True

    def remove_ring(self, index: int):
        if 0 <= index < len(self.rings):
            self.rings.pop(index)

    def move_ring(self, index: int, direction: int):
        j = index + direction
        if 0 <= j < len(self.rings):
            self.rings[index], self.rings[j] = self.rings[j], self.rings[index]

    def clear_rings(self):
        self.rings.clear()
