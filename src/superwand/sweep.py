"""Rendering one image across several k values and themes, and theme x k contact sheets."""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .regions import ImageInput, Regions, load_image, regions_from_array
from .render import render_theme
from .themes import Theme, all_themes, theme_label

MAX_K = 64
_K_TOKEN = re.compile(r"(\d+)(?:\s*-\s*(\d+))?")


def parse_k_values(spec: str | int | Iterable[int]) -> list[int]:
    """
    k values from 4, "4", "2,3,4,6,8", "2-8" or "2-4,8" (ranges are inclusive),
    or an iterable of ints. Returns them sorted and without duplicates.
    """
    if isinstance(spec, int):
        values = [spec]
    elif isinstance(spec, str):
        values = []
        for token in filter(None, (t.strip() for t in spec.split(","))):
            m = _K_TOKEN.fullmatch(token)
            if not m:
                raise ValueError(
                    f"Invalid k {token!r}: use a number, a list like 2,4,8 or a range like 2-8"
                )
            lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
            if hi < lo:
                raise ValueError(f"Invalid k range {token!r}: the end is smaller than the start")
            values.extend(range(lo, hi + 1))
    else:
        values = [int(v) for v in spec]
    if not values:
        raise ValueError("No k values given")
    bad = [v for v in values if not 1 <= v <= MAX_K]
    if bad:
        raise ValueError(f"k must be between 1 and {MAX_K}, got {bad[0]}")
    return sorted(set(values))


@dataclass(frozen=True)
class SweepTile:
    """One rendered combination of a sweep."""

    theme: str
    k: int
    image: Image.Image


def downsample(rgb: Any, alpha: Any, regions: Regions, max_side: int) -> tuple[Any, Any, Regions]:
    """
    A preview-sized copy of (rgb, alpha, regions) made by taking every n-th
    pixel, so previews use exactly the full image's regions.
    """
    h, w = rgb.shape[:2]
    step = max(1, math.ceil(max(h, w) / max_side))
    if step == 1:
        return rgb, alpha, regions
    small = Regions(
        np.ascontiguousarray(regions.labels[::step, ::step]),
        list(regions.colors),
        list(regions.counts),
        regions.centers,
        regions.space,
    )
    small_alpha = None if alpha is None else np.ascontiguousarray(alpha[::step, ::step])
    return np.ascontiguousarray(rgb[::step, ::step]), small_alpha, small


def k_sweep(
    image: ImageInput,
    ks: str | int | Iterable[int],
    themes: Sequence[Theme] | None = None,
    *,
    match: str = "order",
    seed: int = 42,
    space: str = "oklab",
    preview: int | None = None,
    regions_for: Callable[[int], Regions] | None = None,
    **paint_kwargs: Any,
) -> list[SweepTile]:
    """
    Rethemes `image` with every theme at every k. Regions are found once per k
    and reused for all themes. Tiles come back theme by theme, k ascending.

    preview:     if set, paint downsampled copies at most this many pixels on a
                 side (regions still come from the full image)
    regions_for: optional k -> Regions callback, e.g. a cache
    Other keyword arguments go to `paint()` (smooth, shading, gradient, ...).
    """
    rgb, alpha = load_image(image)
    k_values = parse_k_values(ks)
    chosen = list(themes) if themes else list(all_themes())
    tiles = []
    for k in k_values:
        regions = (
            regions_for(k)
            if regions_for
            else regions_from_array(rgb, alpha, k, seed=seed, space=space)
        )
        p_rgb, p_alpha, p_regions = (
            downsample(rgb, alpha, regions, preview) if preview else (rgb, alpha, regions)
        )
        for theme in chosen:
            img = render_theme(p_rgb, p_alpha, p_regions, theme, match=match, **paint_kwargs)
            tiles.append(SweepTile(theme_label(theme), k, img))
    order = {theme_label(t): i for i, t in enumerate(chosen)}
    return sorted(tiles, key=lambda t: (order[t.theme], t.k))


def checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    """Light gray checks, the usual backdrop for transparency."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    checks = ((yy // cell + xx // cell) % 2).astype(bool)
    arr = np.where(checks[..., None], 205, 245).astype(np.uint8).repeat(3, axis=2)
    return Image.fromarray(arr).convert("RGBA")


def contact_sheet(
    tiles: Sequence[SweepTile], cell: int = 200, title: str | None = None
) -> Image.Image:
    """
    A labelled grid of sweep tiles: one row per theme, one column per k.
    `cell` is the longer side of each tile; cells follow the image's aspect ratio.
    """
    if not tiles:
        raise ValueError("No tiles to lay out")
    w0, h0 = tiles[0].image.size
    cell_w, cell_h = (
        (cell, max(1, round(cell * h0 / w0)))
        if w0 >= h0
        else (
            max(1, round(cell * w0 / h0)),
            cell,
        )
    )
    themes = list(dict.fromkeys(t.theme for t in tiles))
    ks = sorted({t.k for t in tiles})
    font_size = max(12, cell // 12)
    font = ImageFont.load_default(size=font_size)
    pad = max(6, cell // 25)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    label_w = max(int(probe.textlength(name, font=font)) for name in themes) + 2 * pad
    header_h = int(font_size * 1.8)
    title_h = header_h if title else 0
    width = label_w + len(ks) * (cell_w + pad) + pad
    height = title_h + header_h + len(themes) * (cell_h + pad) + pad
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    ink = (40, 40, 40)
    if title:
        draw.text((pad, title_h / 2), title, font=font, fill=ink, anchor="lm")
    for col, k in enumerate(ks):
        x = label_w + col * (cell_w + pad) + cell_w / 2
        draw.text((x, title_h + header_h / 2), f"k = {k}", font=font, fill=ink, anchor="mm")
    for row, name in enumerate(themes):
        y = title_h + header_h + row * (cell_h + pad) + cell_h / 2
        draw.text((label_w - pad, y), name, font=font, fill=ink, anchor="rm")
    for tile in tiles:
        row, col = themes.index(tile.theme), ks.index(tile.k)
        thumb = tile.image.convert("RGBA")
        thumb.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
        backdrop = checkerboard(thumb.size)
        backdrop.alpha_composite(thumb)
        x = label_w + col * (cell_w + pad) + (cell_w - thumb.width) // 2
        y = title_h + header_h + row * (cell_h + pad) + (cell_h - thumb.height) // 2
        sheet.paste(backdrop.convert("RGB"), (x, y))
    return sheet
