"""
Color parsing, formatting and conversion between sRGB, OKLab, OKLCh and HSL.

OKLab (https://bottosson.github.io/posts/oklab/) is a perceptual color space:
euclidean distance roughly matches how different two colors look, and its L
channel is perceived lightness. superwand clusters, matches and blends in it.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import numpy.typing as npt

from ._named_colors import NAMED_COLORS

RGB = tuple[int, int, int]
ColorLike = str | Sequence[int]
FloatArray = npt.NDArray[np.floating[Any]]

# A CSS color: #hex, rgb()/rgba()/hsl()/hsla()/oklch()/oklab(), or a named color
CSS_FUNC_RE = re.compile(r"\b(rgba?|hsla?|oklch|oklab)\(([^()]*)\)", re.IGNORECASE)
HEX_RE = re.compile(r"#?([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")


def hex_to_rgb(code: str) -> RGB:
    """'#f80', '#ff8800', '#ff8800cc' (with or without '#') to an RGB tuple."""
    m = HEX_RE.fullmatch(code.strip())
    if not m:
        raise ValueError(f"Invalid hex color {code!r}")
    digits = m.group(1)
    if len(digits) in (3, 4):
        digits = "".join(ch * 2 for ch in digits)
    return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))


def rgb_to_hex(rgb: Sequence[int], upper: bool = False) -> str:
    code = "#{:02x}{:02x}{:02x}".format(*(int(c) for c in rgb[:3]))
    return code.upper() if upper else code


def _clamp8(x: float) -> int:
    return int(max(0, min(255, round(x))))


def _num(token: str, percent_of: float) -> float:
    """A CSS number; percentages are scaled so that 100% == percent_of."""
    token = token.strip().lower()
    if token == "none":
        return 0.0
    if token.endswith("%"):
        return float(token[:-1]) * percent_of / 100
    return float(token)


def _angle(token: str) -> float:
    """A CSS hue in degrees."""
    token = token.strip().lower()
    if token == "none":
        return 0.0
    for unit, scale in (("grad", 0.9), ("turn", 360.0), ("rad", 180 / math.pi), ("deg", 1.0)):
        if token.endswith(unit):
            return float(token[: -len(unit)]) * scale
    return float(token)


def split_args(inner: str) -> tuple[list[str], str | None]:
    """Splits CSS function arguments (comma or space syntax) into components and alpha."""
    inner = inner.strip()
    if "/" in inner:
        main, slash_alpha = inner.split("/", 1)
        return main.replace(",", " ").split(), slash_alpha.strip()
    parts = [p for p in re.split(r"[\s,]+", inner) if p]
    return parts, (parts.pop() if len(parts) == 4 else None)


def parse_css_color(text: str) -> tuple[RGB, str | None] | None:
    """
    Parses one CSS color literal. Returns (rgb, alpha) where alpha is the alpha
    exactly as written (hex digits for #rrggbbaa, else the CSS token), or None
    if `text` isn't a color superwand understands.
    """
    text = text.strip()
    if text.startswith("#"):
        m = HEX_RE.fullmatch(text)
        if not m:
            return None
        digits = m.group(1)
        alpha = None
        if len(digits) == 4:
            alpha = digits[3] * 2
        elif len(digits) == 8:
            alpha = digits[6:]
        return hex_to_rgb(digits), alpha

    named = NAMED_COLORS.get(text.lower())
    if named:
        return hex_to_rgb(named), None

    m = CSS_FUNC_RE.fullmatch(text)
    if not m:
        return None
    func = m.group(1).lower()
    try:
        parts, alpha = split_args(m.group(2))
        if len(parts) != 3:
            return None
        if func.startswith("rgb"):
            rgb = tuple(_clamp8(_num(p, 255)) for p in parts)
        elif func.startswith("hsl"):
            h = _angle(parts[0])
            s, light = (_num(p, 100) / 100 for p in parts[1:])
            rgb = hsl_to_rgb((h, s, light))
        elif func == "oklch":
            lab = oklch_to_oklab((_num(parts[0], 1), _num(parts[1], 0.4), _angle(parts[2])))
            rgb = oklab_to_rgb(lab)
        else:  # oklab
            lab = (_num(parts[0], 1), _num(parts[1], 0.4), _num(parts[2], 0.4))
            rgb = oklab_to_rgb(lab)
    except ValueError:
        return None
    return (int(rgb[0]), int(rgb[1]), int(rgb[2])), alpha


def parse_color(value: ColorLike) -> RGB:
    """
    Accepts '#ff0080', 'ff0080', 'rgb(255 0 128)', 'hsl(330 100% 50%)',
    'oklch(0.65 0.26 0)', 'hotpink', '255,0,128' or a sequence of three ints.
    """
    if not isinstance(value, str):
        if len(value) < 3:
            raise ValueError(f"Invalid color {value!r}: need three channels")
        return (_clamp8(value[0]), _clamp8(value[1]), _clamp8(value[2]))
    text = value.strip()
    if re.fullmatch(r"\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}", text):
        return tuple(_clamp8(int(c)) for c in text.split(","))  # type: ignore[return-value]
    if HEX_RE.fullmatch(text) and text.lower() not in NAMED_COLORS:
        return hex_to_rgb(text)
    parsed = parse_css_color(text)
    if parsed is None:
        raise ValueError(f"Invalid color {value!r}")
    return parsed[0]


def parse_palette(value: str | Iterable[ColorLike]) -> list[RGB]:
    """'#ff0080,#00ffff' (comma or whitespace separated) or an iterable of colors."""
    if isinstance(value, str):
        # Split on commas that aren't inside a CSS function
        tokens, depth, cur = [], 0, ""
        for ch in value:
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and (ch == "," or ch.isspace()):
                if cur:
                    tokens.append(cur)
                cur = ""
            else:
                cur += ch
        if cur:
            tokens.append(cur)
        colors = [parse_color(t) for t in tokens]
    else:
        colors = [parse_color(c) for c in value]
    if not colors:
        raise ValueError("A palette needs at least one color")
    return colors


# --- sRGB <-> OKLab ----------------------------------------------------------

_LMS_FROM_LINEAR = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
_LAB_FROM_LMS = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ]
)
_LMS_FROM_LAB = np.linalg.inv(_LAB_FROM_LMS)
_LINEAR_FROM_LMS = np.linalg.inv(_LMS_FROM_LINEAR)

_LINEAR_LUT = np.where(
    (v := np.arange(256) / 255) <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4
)

_LINEAR_LUT32 = _LINEAR_LUT.astype(np.float32)
_LMS_FROM_LINEAR32 = _LMS_FROM_LINEAR.astype(np.float32)
_LAB_FROM_LMS32 = _LAB_FROM_LMS.astype(np.float32)


def srgb_to_linear(rgb: npt.ArrayLike) -> FloatArray:
    """sRGB in 0..255 to linear light in 0..1."""
    arr = np.asarray(rgb)
    if arr.dtype == np.uint8:
        return _LINEAR_LUT[arr]
    c = arr.astype(np.float64) / 255
    return np.where(c <= 0.04045, c / 12.92, ((np.maximum(c, 0) + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(lin: npt.ArrayLike) -> FloatArray:
    """Linear light in 0..1 to sRGB in 0..255 (unclipped, unrounded)."""
    c = np.clip(np.asarray(lin, dtype=np.float64), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def srgb_to_oklab(rgb: npt.ArrayLike) -> FloatArray:
    """(..., 3) sRGB array in 0..255 to OKLab (L in 0..1)."""
    arr = np.asarray(rgb)
    if arr.dtype == np.uint8:  # whole images: float32 is plenty and twice as fast
        lms = _LINEAR_LUT32[arr] @ _LMS_FROM_LINEAR32.T
        return np.cbrt(lms) @ _LAB_FROM_LMS32.T
    lms = srgb_to_linear(arr) @ _LMS_FROM_LINEAR.T
    return np.cbrt(lms) @ _LAB_FROM_LMS.T


def oklab_to_srgb(lab: npt.ArrayLike) -> FloatArray:
    """(..., 3) OKLab array to sRGB floats in 0..255, clipped to the gamut."""
    lms = (np.asarray(lab, dtype=np.float64) @ _LMS_FROM_LAB.T) ** 3
    return linear_to_srgb(lms @ _LINEAR_FROM_LMS.T)


def to_uint8(arr: npt.ArrayLike) -> npt.NDArray[np.uint8]:
    return np.clip(np.rint(np.asarray(arr, dtype=np.float64)), 0, 255).astype(np.uint8)


def rgb_to_oklab(rgb: Sequence[float]) -> tuple[float, float, float]:
    lab = srgb_to_oklab(np.asarray(rgb[:3], dtype=np.float64))
    return (float(lab[0]), float(lab[1]), float(lab[2]))


def oklab_to_rgb(lab: Sequence[float]) -> RGB:
    rgb = to_uint8(oklab_to_srgb(np.asarray(lab, dtype=np.float64)))
    return (int(rgb[0]), int(rgb[1]), int(rgb[2]))


def oklab_to_oklch(lab: Sequence[float]) -> tuple[float, float, float]:
    L, a, b = lab
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def oklch_to_oklab(lch: Sequence[float]) -> tuple[float, float, float]:
    L, C, h = lch
    return (L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h)))


def lightness(rgb: Sequence[float]) -> float:
    """Perceived lightness (OKLab L, 0..1)."""
    return rgb_to_oklab(rgb)[0]


# --- HSL ---------------------------------------------------------------------


def rgb_to_hsl(rgb: Sequence[int]) -> tuple[float, float, float]:
    """RGB to (hue in degrees, saturation 0..1, lightness 0..1)."""
    r, g, b = (c / 255 for c in rgb[:3])
    hi, lo = max(r, g, b), min(r, g, b)
    light = (hi + lo) / 2
    if hi == lo:
        return (0.0, 0.0, light)
    d = hi - lo
    s = d / (2 - hi - lo) if light > 0.5 else d / (hi + lo)
    if hi == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif hi == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return (h * 60, s, light)


def hsl_to_rgb(hsl: Sequence[float]) -> RGB:
    h, s, light = hsl
    h = (h % 360) / 360
    s = max(0.0, min(1.0, s))
    light = max(0.0, min(1.0, light))
    if s == 0:
        v = _clamp8(light * 255)
        return (v, v, v)
    q = light * (1 + s) if light < 0.5 else light + s - light * s
    p = 2 * light - q

    def channel(t: float) -> float:
        t %= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    return (
        _clamp8(channel(h + 1 / 3) * 255),
        _clamp8(channel(h) * 255),
        _clamp8(channel(h - 1 / 3) * 255),
    )


# --- WCAG contrast -----------------------------------------------------------


def relative_luminance(rgb: Sequence[int]) -> float:
    """WCAG 2 relative luminance, 0 (black) to 1 (white)."""
    lin = srgb_to_linear(np.asarray(rgb[:3], dtype=np.float64))
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


def contrast_ratio(fg: Sequence[int], bg: Sequence[int]) -> float:
    """WCAG 2 contrast ratio, 1 to 21. 4.5 is the AA minimum for body text."""
    a, b = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def ensure_contrast(fg: Sequence[int], bg: Sequence[int], minimum: float = 4.5) -> RGB:
    """
    Returns `fg` with its OKLab lightness moved away from `bg` just far enough
    to reach `minimum` contrast, keeping hue and chroma where the gamut allows.
    Falls back to black or white when no lightness of that hue gets there.
    """
    fg = tuple(int(c) for c in fg[:3])
    if contrast_ratio(fg, bg) >= minimum:
        return fg  # type: ignore[return-value]
    L, a, b = rgb_to_oklab(fg)
    go_dark = relative_luminance(bg) > 0.18  # light background: darken the text
    lo, hi = (0.0, L) if go_dark else (L, 1.0)
    best: RGB | None = None
    for _ in range(24):
        mid = (lo + hi) / 2
        cand = oklab_to_rgb((mid, a, b))
        if contrast_ratio(cand, bg) >= minimum:
            best = cand
            lo, hi = (mid, hi) if go_dark else (lo, mid)
        else:
            lo, hi = (lo, mid) if go_dark else (mid, hi)
    if best is not None:
        return best
    black, white = (0, 0, 0), (255, 255, 255)
    return black if contrast_ratio(black, bg) >= contrast_ratio(white, bg) else white
