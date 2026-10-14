"""Gradient geometry and color blending."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

from .color import FloatArray, oklab_to_srgb, srgb_to_oklab

GRADIENT_STYLES = (
    "none",
    "auto",
    "vertical",
    "horizontal",
    "radial",
    "bottom-up",
    "top-down",
    "left-right",
    "right-left",
)

# UI / CLI aliases for the canonical gradient directions
STYLE_ALIASES = {
    "auto": "top-down",
    "vertical": "top-down",
    "horizontal": "left-right",
}

Point = tuple[float, float]


def normalize_style(style: str | None) -> str | None:
    """Canonical gradient direction, or None for no gradient."""
    if not style or style == "none":
        return None
    style = STYLE_ALIASES.get(style, style)
    if style not in GRADIENT_STYLES:
        raise ValueError(f"Unsupported gradient style {style!r}; choose from {GRADIENT_STYLES}")
    return style


def twod_dist(p1: Sequence[float], p2: Sequence[float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def calc_gradient_poles(
    grad_kw: str,
    pixel_arr: npt.ArrayLike | None,
    img_size: tuple[int, int] | None = None,
) -> tuple[Point, Point]:
    """
    Returns (start_pole, end_pole) as (x, y) points. With img_size the poles
    span the whole image; otherwise they span the bounding box of pixel_arr
    (a sequence of [x, y] points).
    """
    if img_size:
        w, h = img_size
        match grad_kw:
            case "bottom-up":
                return (w / 2, h - 1), (w / 2, 0)
            case "top-down":
                return (w / 2, 0), (w / 2, h - 1)
            case "left-right":
                return (0, h / 2), (w - 1, h / 2)
            case "right-left":
                return (w - 1, h / 2), (0, h / 2)
            case "radial":
                return (w / 2, h / 2), (w - 1, h - 1)
            case _:
                raise ValueError(f"Unsupported gradient keyword {grad_kw}")

    pts = np.asarray(pixel_arr, dtype=np.float64).reshape(-1, 2)
    xs, ys = pts[:, 0], pts[:, 1]
    x_lo, x_hi, y_lo, y_hi = (float(f(v)) for v in (xs, ys) for f in (np.min, np.max))
    mid_x, mid_y = (x_lo + x_hi) / 2, (y_lo + y_hi) / 2
    match grad_kw:
        case "bottom-up":
            return (mid_x, y_hi), (mid_x, y_lo)
        case "top-down":
            return (mid_x, y_lo), (mid_x, y_hi)
        case "left-right":
            return (x_lo, mid_y), (x_hi, mid_y)
        case "right-left":
            return (x_hi, mid_y), (x_lo, mid_y)
        case "radial":
            center = pts.mean(axis=0)
            farthest = pts[np.argmax(np.hypot(xs - center[0], ys - center[1]))]
            return (float(center[0]), float(center[1])), (float(farthest[0]), float(farthest[1]))
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")


def polarity_exponent(polarity: float) -> float:
    """
    Exponent p such that factor ** p == 0.5 when factor == polarity, i.e.
    polarity is how far along the gradient the 50/50 blend lands.
    """
    safe = max(0.001, min(0.999, polarity))
    if safe == 0.5:
        return 1.0
    return math.log(0.5) / math.log(safe)


def gradient_factors(
    rows: npt.ArrayLike,
    cols: npt.ArrayLike,
    grad_kw: str,
    start_pole: Sequence[float],
    end_pole: Sequence[float],
    polarity: float = 0.5,
) -> npt.NDArray[np.float64] | None:
    """
    Position of each (row, col) pixel along the gradient, in [0, 1].
    Returns None when the poles are degenerate (zero-length gradient).
    """
    r = np.asarray(rows, dtype=np.float64)
    c = np.asarray(cols, dtype=np.float64)
    spx, spy = float(start_pole[0]), float(start_pole[1])
    epx, epy = float(end_pole[0]), float(end_pole[1])

    match grad_kw:
        case "left-right" | "right-left":
            if abs(epx - spx) < 1e-6:
                return None
            factor = (c - spx) / (epx - spx)
        case "top-down" | "bottom-up":
            if abs(epy - spy) < 1e-6:
                return None
            factor = (r - spy) / (epy - spy)
        case "radial":
            max_dist = twod_dist(start_pole, end_pole)
            if max_dist < 1e-6:
                return None
            factor = np.hypot(c - spx, r - spy) / max_dist
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")

    factor = np.clip(factor, 0, 1)
    p = polarity_exponent(polarity)
    return factor**p if p != 1.0 else factor


def blend_colors(
    start_color: Sequence[int],
    end_color: Sequence[int],
    factor: npt.NDArray[np.float64],
    space: str = "oklab",
) -> FloatArray:
    """
    Per-pixel blend from start to end, returned as (N, 3) sRGB floats.
    Blending in OKLab keeps midpoints vivid (blue to yellow doesn't pass
    through gray); space="srgb" blends the raw channel values.
    """
    f = np.asarray(factor, dtype=np.float64)[:, np.newaxis]
    if space == "srgb":
        sc = np.asarray(start_color[:3], dtype=np.float64)
        ec = np.asarray(end_color[:3], dtype=np.float64)
        return sc + (ec - sc) * f
    s_lab = srgb_to_oklab(np.asarray(start_color[:3], dtype=np.float64))
    e_lab = srgb_to_oklab(np.asarray(end_color[:3], dtype=np.float64))
    return oklab_to_srgb(s_lab + (e_lab - s_lab) * f)


def clamp(n: float, smallest: float, largest: float) -> float:
    return max(smallest, min(n, largest))


def adjust_color(color: Sequence[int], factor: float) -> tuple[int, int, int]:
    """Scales each channel by `factor`, clamped to 0..255."""
    r, g, b = color[:3]
    return (
        int(clamp(int(r * factor), 0, 255)),
        int(clamp(int(g * factor), 0, 255)),
        int(clamp(int(b * factor), 0, 255)),
    )
