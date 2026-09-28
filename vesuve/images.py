"""The images a pipeline renders: a mask in colours, an overlay, a scale bar.

PNG and TIFF written by Pillow and tifffile, nothing more. ⚠ An image is a VIEW: what a pipeline concludes is in
its report, and an image one would have to read to know something is a defect.
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw

# absent, present not certified, certified, suspect (surrounded by a loop that crosses)
COLOURS = np.array([[18, 18, 24], [92, 96, 110], [70, 190, 140], [230, 120, 60]], dtype=np.uint8)


def mask_in_colours(mask: np.ndarray, enlarge: int = 2) -> Image.Image:
    rgb = COLOURS[np.clip(mask, 0, len(COLOURS) - 1)]
    im = Image.fromarray(rgb, "RGB")
    return im.resize((im.width * enlarge, im.height * enlarge), Image.NEAREST)


def overlay(background: np.ndarray, mask: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """The per-chunk mask, stretched to the size of the background (an ink map, a render), in transparency."""
    f = np.asarray(background, dtype=np.float32)
    if f.ndim == 3:
        f = f.mean(axis=2)
    low, high = np.percentile(f, [1, 99])
    g = np.clip((f - low) / max(high - low, 1e-9), 0, 1)
    base = np.stack([g * 255] * 3, axis=-1)
    m = np.asarray(Image.fromarray(mask.astype(np.uint8)).resize((f.shape[1], f.shape[0]), Image.NEAREST))
    tint = COLOURS[np.clip(m, 0, len(COLOURS) - 1)].astype(np.float32)
    coloured = m >= 2
    base[coloured] = (1 - alpha) * base[coloured] + alpha * tint[coloured]
    return Image.fromarray(base.astype(np.uint8), "RGB")


def grey_levels(image: np.ndarray, low_pct: float = 1.0, high_pct: float = 99.0) -> Image.Image:
    """A greyscale image, stretched between two percentiles (`couche_de_rendu.py:35`: 1 and 99)."""
    a = np.asarray(image, dtype=np.float32)
    ok = np.isfinite(a)
    low, high = np.percentile(a[ok], [low_pct, high_pct]) if ok.any() else (0.0, 1.0)
    g = np.clip((np.where(ok, a, low) - low) / max(high - low, 1e-9), 0, 1)
    return Image.fromarray((g * 255).astype(np.uint8), "L")


def scale_bar(im: Image.Image, pixel_um: float, length_mm: float = 10.0) -> Image.Image:
    """A bar of `length_mm` at the bottom left, as First Letters requires (1 cm)."""
    im = im.convert("RGB")
    n = int(round(length_mm * 1000.0 / pixel_um))
    d = ImageDraw.Draw(im)
    h = max(4, im.height // 150)
    x0, y0 = im.width // 40, im.height - im.height // 30 - h
    d.rectangle([x0, y0, x0 + n, y0 + h], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((x0, y0 - 14), f"{length_mm:g} mm", fill=(255, 255, 255))
    return im


def read_image(data: bytes) -> np.ndarray:
    Image.MAX_IMAGE_PIXELS = None  # a segment's ink map exceeds Pillow's decompression-bomb guard
    return np.asarray(Image.open(io.BytesIO(data)).convert("L"))


LOOP_STATES = {"under": (70, 190, 140), "crosses": (230, 120, 60), "to read": (120, 170, 230),
               "unseen": (200, 200, 90), "open": (180, 90, 180)}


def draw_loops(im: Image.Image, journal, pixels_per_chunk: float, thickness: int = 2) -> Image.Image:
    """The outline of each loop of the journal, in the colour of its state: what holds, what crosses, and what is
    left to read. A loop is drawn at its corners; the legend is in the report."""
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)
    order = {"to read": 0, "open": 1, "unseen": 1, "crosses": 2, "under": 3}
    for e in sorted(journal, key=lambda e: order.get(e.get("state"), 0)):
        co, state = e.get("corners"), e.get("state")
        if not co or state not in LOOP_STATES:
            continue
        r0, r1, c0, c1 = co
        k = pixels_per_chunk
        d.rectangle([c0 * k, r0 * k, (c1 + 1) * k - 1, (r1 + 1) * k - 1], outline=LOOP_STATES[state],
                    width=thickness + (1 if state in ("under", "crosses") else 0))
    return im
