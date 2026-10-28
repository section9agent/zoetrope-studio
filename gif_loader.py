"""
gif_loader.py
Extracts individual frames from a GIF using Pillow with full disposal compositing.
Returns a list of QImage (RGBA).
"""
from __future__ import annotations
from typing import List

from PIL import Image, ImageSequence
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt


def pil_to_qimage(pil_img: Image.Image) -> QImage:
    """Convert a Pillow RGBA image to QImage Format_RGBA8888."""
    img = pil_img.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, img.width * 4, QImage.Format.Format_RGBA8888)
    return qimg.copy()   # .copy() detaches from the Python buffer


def load_gif(path: str) -> List[QImage]:
    """
    Load all frames from a GIF file with correct disposal compositing.
    Returns a list of QImage frames in RGBA format.
    Falls back gracefully: if anything fails, returns a single-frame list.
    """
    try:
        with Image.open(path) as src:
            width, height = src.size
            frames: List[QImage] = []

            # Canvas for compositing (handles disposal modes 0, 1, 2, 3)
            canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            prev_canvas = canvas.copy()

            for frame_idx, frame in enumerate(ImageSequence.Iterator(src)):
                info = frame.info
                disposal = info.get("disposal", 0)

                # Work on a copy of the canvas
                working = canvas.copy()

                # Convert this frame to RGBA
                frame_rgba = frame.convert("RGBA")

                # Get frame position (GIF frames can be sub-rectangles)
                offset = (info.get("x_offset", 0), info.get("y_offset", 0))

                # Composite frame onto working canvas
                working.paste(frame_rgba, offset, frame_rgba)

                frames.append(pil_to_qimage(working))

                # Apply disposal mode for next frame
                if disposal == 2:
                    # Restore to background (clear)
                    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                elif disposal == 3:
                    # Restore to previous
                    canvas = prev_canvas.copy()
                else:
                    # 0 or 1: keep current canvas
                    prev_canvas = working.copy()
                    canvas = working

            return frames if frames else _fallback(path)

    except Exception:
        return _fallback(path)


def _fallback(path: str) -> List[QImage]:
    """Last-resort: load the file as a plain image."""
    try:
        img = Image.open(path).convert("RGBA")
        return [pil_to_qimage(img)]
    except Exception:
        return []


def load_static_image(path: str) -> List[QImage]:
    """Load a single static image (PNG, JPG, etc.) as a one-frame list."""
    try:
        with Image.open(path) as img:
            return [pil_to_qimage(img.convert("RGBA"))]
    except Exception:
        return []
