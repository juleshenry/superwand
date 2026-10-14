"""
Built-in themes, user theme files, and how palette colors are assigned to
image regions.

A theme can be given as a built-in name ("Neon", case-insensitive), the name
of a theme file in the user themes directory, a path to a palette file
(.json, .toml, .gpl, .ase, .hex, .txt, .css), a color list string such as
"#ff0080,#00ffff,navy", or a sequence of colors.
"""

from __future__ import annotations

import os
import sys
import unicodedata
import warnings
from collections.abc import Sequence
from pathlib import Path

from .color import RGB, ColorLike, lightness, parse_palette
from .palette_io import READ_EXTENSIONS, load_palette

MATCH_MODES = ("order", "luminance")

Theme = str | Sequence[ColorLike]

color_themes: dict[str, list[RGB]] = {
    "Spring": [
        (132, 255, 163),
        (255, 212, 77),
        (124, 252, 0),
        (255, 250, 205),
        (255, 182, 193),
        (173, 255, 47),
        (255, 105, 180),
        (240, 255, 240),
    ],
    "Summer": [
        (255, 215, 0),
        (0, 191, 255),
        (46, 139, 87),
        (255, 140, 0),
        (255, 99, 71),
        (255, 182, 193),
        (255, 20, 147),
        (32, 178, 170),
    ],
    "Winter": [
        (173, 216, 230),
        (240, 248, 255),
        (0, 0, 128),
        (135, 206, 250),
        (255, 250, 250),
        (70, 130, 180),
        (176, 224, 230),
        (0, 255, 255),
    ],
    "Fall": [
        (255, 69, 0),
        (218, 165, 32),
        (128, 0, 0),
        (255, 99, 71),
        (160, 82, 45),
        (139, 69, 19),
        (255, 140, 0),
        (205, 133, 63),
    ],
    "Safari": [
        (139, 69, 19),
        (154, 205, 50),
        (205, 133, 63),
        (139, 121, 94),
        (238, 232, 170),
        (240, 230, 140),
        (189, 183, 107),
        (160, 82, 45),
    ],
    "Urban": [
        (149, 145, 140),
        (135, 135, 135),
        (99, 102, 94),
        (64, 66, 59),
        (189, 183, 107),
        (128, 128, 128),
        (169, 169, 169),
        (211, 211, 211),
    ],
    "Neon": [
        (255, 105, 195),
        (70, 130, 195),
        (50, 205, 65),
        (255, 255, 15),
        (255, 20, 147),
        (138, 43, 226),
        (0, 255, 255),
        (255, 165, 0),
    ],
    "Tropical": [
        (255, 165, 0),
        (255, 69, 0),
        (50, 205, 50),
        (30, 144, 255),
        (255, 218, 185),
        (255, 99, 71),
        (0, 255, 255),
        (255, 105, 180),
    ],
    "Arctic": [
        (240, 255, 255),
        (173, 216, 230),
        (135, 206, 250),
        (70, 130, 180),
        (255, 250, 250),
        (224, 255, 255),
        (0, 191, 255),
        (176, 224, 230),
    ],
    "Paixão": [
        (255, 101, 45),
        (255, 69, 109),
        (255, 85, 255),
        (255, 20, 147),
        (255, 105, 180),
        (219, 112, 147),
        (238, 130, 238),
        (255, 182, 193),
    ],
    "Cyberpunk": [
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 0),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
    ],
    "Midnight": [
        (25, 25, 112),
        (0, 0, 128),
        (0, 0, 139),
        (0, 0, 205),
        (65, 105, 225),
        (70, 130, 180),
        (72, 61, 139),
        (106, 90, 205),
    ],
    "Forest": [
        (34, 139, 34),
        (0, 100, 0),
        (0, 128, 0),
        (46, 139, 87),
        (60, 179, 113),
        (32, 178, 170),
        (107, 142, 35),
        (85, 107, 47),
    ],
    "Sunset": [
        (255, 69, 0),
        (255, 140, 0),
        (255, 165, 0),
        (255, 215, 0),
        (255, 127, 80),
        (255, 99, 71),
        (255, 160, 122),
        (250, 128, 114),
    ],
    "Oceanic": [
        (0, 105, 148),
        (0, 128, 128),
        (0, 206, 209),
        (64, 224, 208),
        (72, 209, 204),
        (127, 255, 212),
        (0, 191, 255),
        (176, 224, 230),
    ],
    "Vaporwave": [
        (255, 113, 206),
        (1, 205, 254),
        (5, 255, 161),
        (185, 103, 255),
        (255, 251, 150),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ],
    "Retro80s": [
        (255, 0, 128),
        (0, 255, 255),
        (128, 0, 255),
        (255, 255, 0),
        (0, 0, 0),
        (255, 255, 255),
        (255, 128, 0),
        (0, 255, 0),
    ],
    "Volcano": [
        (60, 0, 0),
        (120, 0, 0),
        (180, 0, 0),
        (255, 0, 0),
        (255, 69, 0),
        (255, 140, 0),
        (255, 165, 0),
        (0, 0, 0),
    ],
}


def themes_dir() -> Path:
    """
    Where user themes live: $SUPERWAND_THEMES_DIR, else
    $XDG_CONFIG_HOME/superwand/themes (~/.config/superwand/themes), or
    %APPDATA%\\superwand\\themes on Windows.
    """
    if env := os.environ.get("SUPERWAND_THEMES_DIR"):
        return Path(env).expanduser()
    if sys.platform == "win32" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "superwand" / "themes"
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "superwand" / "themes"


def user_themes() -> dict[str, list[RGB]]:
    """Themes loaded from palette files in `themes_dir()`."""
    folder = themes_dir()
    themes: dict[str, list[RGB]] = {}
    if not folder.is_dir():
        return themes
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in READ_EXTENSIONS:
            continue
        try:
            name, colors = load_palette(path)
        except (OSError, ValueError) as e:
            warnings.warn(f"Skipping theme file {path}: {e}", stacklevel=2)
            continue
        themes[name] = colors
    return themes


def all_themes() -> dict[str, list[RGB]]:
    """Built-in themes plus user themes (a user theme replaces a built-in of the same name)."""
    return {**color_themes, **user_themes()}


def _key(name: str) -> str:
    """Case- and accent-insensitive lookup key, so 'paixao' finds 'Paixão'."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return ascii_name.casefold().strip()


def find_theme(name: str) -> tuple[str, list[RGB]] | None:
    """Looks up a theme by name; returns (canonical name, colors) or None."""
    themes = all_themes()
    if name in themes:
        return name, list(themes[name])
    wanted = _key(name)
    for candidate, colors in themes.items():
        if _key(candidate) == wanted:
            return candidate, list(colors)
    return None


def resolve_theme(theme: Theme) -> list[RGB]:
    """Turns any accepted theme form (see module docstring) into a list of RGB tuples."""
    return _resolve(theme)[1]


def theme_label(theme: Theme) -> str:
    """A short name for output files: the theme name, palette file name, or 'custom'."""
    return _resolve(theme)[0]


def _resolve(theme: Theme) -> tuple[str, list[RGB]]:
    if not isinstance(theme, str):
        return "custom", parse_palette(theme)
    found = find_theme(theme)
    if found:
        return found
    path = Path(theme).expanduser()
    if path.suffix.lower() in READ_EXTENSIONS and path.is_file():
        return load_palette(path)
    try:
        return "custom", parse_palette(theme)
    except ValueError:
        pass
    raise ValueError(
        f"Unknown theme {theme!r}. Use a theme name ({', '.join(all_themes())}), "
        "a palette file, or a color list like '#ff0080,#00ffff'."
    )


def match_palette(
    region_colors: Sequence[Sequence[int]], palette: Sequence[Sequence[int]], match: str = "order"
) -> list[RGB]:
    """
    Assigns one palette color per region.

    - "order": region i (by prominence) gets palette[i], cycling if the palette is short.
    - "luminance": the darkest region gets the darkest palette color and so on,
      which preserves the image's light and shadow.
    """
    if match not in MATCH_MODES:
        raise ValueError(f"match must be one of {MATCH_MODES}, got {match!r}")
    colors = [(int(c[0]), int(c[1]), int(c[2])) for c in palette]
    if not colors:
        raise ValueError("palette must contain at least one color")

    n = len(region_colors)
    chosen = [colors[i % len(colors)] for i in range(n)]
    if match == "order":
        return chosen

    regions_by_lightness = sorted(range(n), key=lambda i: lightness(region_colors[i]))
    colors_by_lightness = sorted(chosen, key=lightness)
    assigned: list[RGB] = [colors[0]] * n
    for region_idx, color in zip(regions_by_lightness, colors_by_lightness, strict=True):
        assigned[region_idx] = color
    return assigned
