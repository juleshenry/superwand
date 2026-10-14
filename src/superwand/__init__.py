"""
superwand: retheme images, SVG and CSS with color palettes and gradients.

    >>> from superwand import retheme
    >>> retheme("charizard.png", "Vaporwave", k=6).save("out.png")
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from .color import parse_color, parse_palette
from .css import css_retheme
from .gif import theme_cycle_gif
from .palette_io import load_palette, save_palette
from .regions import Regions, extract_palette, find_regions
from .render import (
    gradient_enforce,
    paint,
    render_theme,
    retheme,
    retheme_file,
    transfer_palette,
)
from .svg import svg_retheme
from .sweep import SweepTile, contact_sheet, k_sweep, parse_k_values
from .themes import all_themes, color_themes, match_palette, resolve_theme, themes_dir

try:
    __version__ = version("superwand")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0+unknown"

__all__ = [
    "Regions",
    "SweepTile",
    "__version__",
    "all_themes",
    "color_themes",
    "contact_sheet",
    "css_retheme",
    "extract_palette",
    "find_regions",
    "gradient_enforce",
    "k_sweep",
    "load_palette",
    "match_palette",
    "paint",
    "parse_color",
    "parse_k_values",
    "parse_palette",
    "render_theme",
    "resolve_theme",
    "retheme",
    "retheme_file",
    "save_palette",
    "svg_retheme",
    "theme_cycle_gif",
    "themes_dir",
    "transfer_palette",
]

_DEPRECATED = {"SuperWand", "np_get_prominent_regions", "np_inject_theme"}


def __getattr__(name: str) -> Any:
    if name in _DEPRECATED:
        from . import _compat  # each name warns when it's used

        return getattr(_compat, name)
    raise AttributeError(f"module 'superwand' has no attribute {name!r}")
