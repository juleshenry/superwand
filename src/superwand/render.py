"""Repainting image regions with theme colors and gradients."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path
from typing import Any, cast

import numpy as np
import numpy.typing as npt
from PIL import Image
from scipy.ndimage import binary_closing, binary_dilation

from .color import (
    RGB,
    ColorLike,
    FloatArray,
    oklab_to_srgb,
    parse_color,
    srgb_to_oklab,
    to_uint8,
)
from .gradients import (
    adjust_color,
    blend_colors,
    calc_gradient_poles,
    gradient_factors,
    normalize_style,
)
from .regions import (
    ImageInput,
    Regions,
    U8Array,
    extract_palette,
    load_image,
    regions_from_array,
)
from .themes import Theme, match_palette, resolve_theme, theme_label

GradientPair = tuple[RGB, RGB]
Target = RGB | GradientPair | None
PerRegion = str | None | Sequence[str | None]

GRADIENT_INTENSITY = 0.2  # brightness swing of a gradient made from a single color
BAND_PIXELS = 1 << 19  # paint in row bands of about this many pixels to bound memory


def _is_pair(target: object) -> bool:
    return (
        isinstance(target, (list, tuple))
        and len(target) == 2
        and isinstance(target[0], (list, tuple, np.ndarray))
    )


def _as_pair(target: object) -> tuple[RGB, RGB | None] | None:
    """A target as (start, end), where end is None for a single color."""
    if target is None:
        return None
    if _is_pair(target):
        pair = cast(Sequence[ColorLike], target)
        return parse_color(pair[0]), parse_color(pair[1])
    return parse_color(cast(ColorLike, target)), None


def _per_region(value: object, n: int, default: Any) -> list[Any]:
    if isinstance(value, (list, tuple)):
        return [value[i] if i < len(value) and value[i] is not None else default for i in range(n)]
    return [default if value is None else value] * n


def paint(
    rgb: U8Array,
    alpha: U8Array | None,
    regions: Regions,
    targets: Sequence[Target],
    *,
    gradient: PerRegion = None,
    polarity: float | Sequence[float | None] = 0.5,
    flood: bool = False,
    smooth: bool = False,
    shading: bool = False,
) -> Image.Image:
    """
    Repaints each region of `rgb` with its target and returns an RGBA image.

    targets:  one per region: an RGB color, a (start, end) gradient pair, or
              None to keep the region's original pixels.
    gradient: a style for every region or one per region. A single-color
              target with a gradient blends into the next region's target
              (or a lighter/darker version of itself if there is none).
    polarity: where the 50/50 blend of a gradient lands (0..1), global or per region.
    flood:    close holes and grow each region before painting.
    smooth:   blend edge pixels between their two nearest regions' colors,
              which keeps anti-aliased edges smooth.
    shading:  keep each pixel's lightness relative to its region, so texture
              and shadows survive the recolor.
    """
    if flood and smooth:
        raise ValueError("flood and smooth can't be combined")
    n = len(regions)
    h, w = rgb.shape[:2]
    # Normalize each target to (start color, end color or None), or None to keep the region
    pairs: list[tuple[RGB, RGB | None] | None] = [
        _as_pair(targets[i]) if i < len(targets) else None for i in range(n)
    ]
    styles = [normalize_style(s) for s in _per_region(gradient, n, None)]
    polarities = [float(p) for p in _per_region(polarity, n, 0.5)]
    poles = {s: calc_gradient_poles(s, None, img_size=(w, h)) for s in set(styles) if s}
    region_l = regions.lightness

    def colors_for(
        i: int, rows: npt.NDArray[np.intp], cols: npt.NDArray[np.intp], pixel_l: FloatArray | None
    ) -> FloatArray | None:
        """Target colors for pixels (rows, cols) painted as region i, or None to keep them."""
        pair = pairs[i]
        if pair is None:
            return None
        start, end = pair
        style = styles[i]
        factor = None
        if style is not None:
            if end is None:
                nxt = pairs[(i + 1) % n] if n > 1 else None
                if nxt is not None:
                    end = nxt[0]
                else:
                    start = adjust_color(start, 1 + GRADIENT_INTENSITY)
                    end = adjust_color(pair[0], 1 - GRADIENT_INTENSITY)
            factor = gradient_factors(rows, cols, style, *poles[style], polarities[i])
        out: FloatArray
        if factor is None or end is None:
            out = np.broadcast_to(np.asarray(start, dtype=np.float64), (len(rows), 3))
        else:
            out = blend_colors(start, end, factor)
        if pixel_l is not None:
            lab = srgb_to_oklab(np.asarray(out, dtype=np.float64))
            lab[:, 0] += pixel_l - region_l[i]
            out = oklab_to_srgb(lab)
        return out

    labels = regions.labels
    if flood:
        # Each region grows over its neighbours; later (smaller) regions win overlaps
        labels = labels.copy()
        for i in range(n):
            grown = binary_dilation(binary_closing(regions.labels == i, iterations=2), iterations=3)
            labels[grown] = i

    result = rgb.copy()
    if not shading and not (smooth and n > 1) and not any(styles):
        # Flat colors only: one vectorized lookup instead of per-region work
        lut = np.zeros((max(n, 1), 3), dtype=np.uint8)
        keep = np.ones(max(n, 1), dtype=bool)
        for i, pair in enumerate(pairs):
            if pair is not None:
                lut[i], keep[i] = pair[0], False
        repaint = (labels >= 0) & ~keep[np.maximum(labels, 0)]
        result[repaint] = lut[labels[repaint]]
    else:
        layers = [labels]
        weight = None
        if smooth and n > 1:
            second, weight = regions.soft_assignment(rgb)
            layers.append(second)
        band = max(1, BAND_PIXELS // max(w, 1))
        for r0 in range(0, h, band):
            r1 = min(h, r0 + band)
            src = rgb[r0:r1]
            band_l = srgb_to_oklab(src)[..., 0] if shading else None
            painted = []
            for layer_labels in layers:
                layer = src.astype(np.float64)
                lb = layer_labels[r0:r1]
                for i in range(n):
                    rows, cols = np.nonzero(lb == i)
                    if len(rows) == 0:
                        continue
                    pl = band_l[rows, cols] if band_l is not None else None
                    colors = colors_for(i, rows + r0, cols, pl)
                    if colors is not None:
                        layer[rows, cols] = colors
                painted.append(layer)
            out = painted[0]
            if weight is not None:
                wt = weight[r0:r1, :, None]
                out = painted[0] * wt + painted[1] * (1 - wt)
            visible = labels[r0:r1] >= 0
            result[r0:r1][visible] = to_uint8(out[visible])

    a = np.full((h, w), 255, dtype=np.uint8) if alpha is None else alpha
    return Image.fromarray(np.dstack([result, a]), "RGBA")


def _coerce_regions(regions: object, shape: tuple[int, int]) -> Regions | None:
    if regions is None or isinstance(regions, Regions):
        return regions
    if isinstance(regions, Mapping):  # pre-0.4 {color: [[row, col], ...]}
        return Regions.from_dict(regions, shape)
    raise TypeError(f"regions must be a Regions object, got {type(regions).__name__}")


def _apply_overrides(
    targets: list[Target], overrides: Mapping[int, ColorLike | None] | None
) -> list[Target]:
    for index, color in (overrides or {}).items():
        if not -len(targets) <= index < len(targets):
            raise IndexError(f"No region {index}: the image has {len(targets)} regions")
        targets[index] = None if color is None else parse_color(color)
    return targets


def render_theme(
    rgb: U8Array,
    alpha: U8Array | None,
    regions: Regions,
    theme: Theme,
    *,
    match: str = "order",
    overrides: Mapping[int, ColorLike | None] | None = None,
    **paint_kwargs: Any,
) -> Image.Image:
    """Paints already-found regions with a theme: match colors, apply overrides, paint."""
    targets: list[Target] = list(match_palette(regions.colors, resolve_theme(theme), match))
    return paint(rgb, alpha, regions, _apply_overrides(targets, overrides), **paint_kwargs)


def retheme(
    image: ImageInput,
    theme: Theme,
    k: int = 4,
    flood: bool = False,
    gradient: PerRegion = None,
    polarity: float = 0.5,
    match: str = "order",
    regions: Regions | None = None,
    *,
    smooth: bool = False,
    shading: bool = False,
    overrides: Mapping[int, ColorLike | None] | None = None,
    space: str = "oklab",
    seed: int = 42,
) -> Image.Image:
    """
    Rethemes an image and returns the result as an RGBA PIL Image.
    Transparent pixels stay transparent.

    image:     path or PIL Image
    theme:     theme name, palette file, "#hex,#hex" string, or list of colors
    k:         number of color regions to find
    gradient:  None or a gradient style (radial, top-down, left-right, ...)
    polarity:  where the 50/50 blend of a gradient lands (0.0 to 1.0)
    match:     "order" maps regions to theme colors by prominence,
               "luminance" maps the darkest region to the darkest color, and so on
    regions:   precomputed `find_regions` output, to reuse across calls
    smooth:    blend edge pixels between neighboring regions (anti-aliasing)
    shading:   keep each pixel's lightness offset, so photos keep their texture
    overrides: {region index: color or None} to pin a region to a color, or
               keep its original pixels with None; index 0 is the largest region
    space:     color space for finding regions, "oklab" or "rgb"
    seed:      k-means seed; the same seed always gives the same regions
    """
    rgb, alpha = load_image(image)
    found = _coerce_regions(regions, (rgb.shape[0], rgb.shape[1])) or regions_from_array(
        rgb, alpha, k, seed=seed, space=space
    )
    return render_theme(
        rgb,
        alpha,
        found,
        theme,
        match=match,
        overrides=overrides,
        gradient=gradient,
        polarity=polarity,
        flood=flood,
        smooth=smooth,
        shading=shading,
    )


def transfer_palette(
    image: ImageInput, reference: ImageInput, k: int = 4, match: str = "luminance", **kwargs: object
) -> Image.Image:
    """Rethemes `image` with the k dominant colors of `reference`."""
    return retheme(image, extract_palette(reference, k), k=k, match=match, **kwargs)  # type: ignore[arg-type]


def retheme_file(
    image_path: str | PathLike[str],
    theme: Theme,
    output_dir: str | PathLike[str] = ".",
    *,
    label: str | None = None,
    **kwargs: object,
) -> Path:
    """Rethemes an image file and saves it as <output_dir>/<stem>_<label>.png."""
    path = Path(image_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{path.stem}_{label or theme_label(theme)}.png"
    retheme(path, theme, **kwargs).save(out)  # type: ignore[arg-type]
    return out


def gradient_enforce(
    img: ImageInput,
    style: str = "auto",
    completeness: str | None = None,
    opacity: str | None = None,
    color1: ColorLike | None = None,
    color2: ColorLike | None = None,
    polarity: float = 0.5,
    number: int = 4,
) -> Image.Image:
    """
    Turns each flat color region into a gradient: from color1 to color2 when
    both are given, otherwise from a lighter to a darker version of the
    region's own color. Returns RGB, or RGBA when the input has transparency.
    `completeness` and `opacity` are deprecated and ignored.
    """
    if completeness is not None or opacity is not None:
        import warnings

        warnings.warn(
            "gradient_enforce(): completeness and opacity never had an effect and will be removed",
            DeprecationWarning,
            stacklevel=2,
        )
    rgb, alpha = load_image(img)
    found = regions_from_array(rgb, alpha, number)
    if color1 is not None and color2 is not None:
        pair = (parse_color(color1), parse_color(color2))
        targets: list[Target] = [pair] * len(found)
    else:
        targets = [
            (adjust_color(c, 1 + GRADIENT_INTENSITY), adjust_color(c, 1 - GRADIENT_INTENSITY))
            for c in found.colors
        ]
    out = paint(rgb, alpha, found, targets, gradient=style or "auto", polarity=polarity)
    return out if alpha is not None else out.convert("RGB")
