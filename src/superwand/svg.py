"""
Retheme the colors in an SVG document.

Colors are found in presentation attributes (fill, stroke, stop-color,
flood-color, lighting-color, color), in style="..." attributes and in <style>
elements, then clustered and mapped to a palette exactly like stylesheets
(see superwand.css). Comments, ids, url(#refs), none and currentColor are left
alone, and the rest of the document is preserved byte for byte.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from .color import parse_css_color
from .css import DEFAULT_THEME, ColorToken, Source, read_source, recolor_tokens, scan_css
from .themes import Theme

COLOR_ATTRIBUTES = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color")

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_STYLE_ELEMENT_RE = re.compile(r"<style\b[^>]*>(.*?)</style\s*>", re.DOTALL | re.IGNORECASE)
_ATTR_RE = re.compile(
    r"(?<=\s)(" + "|".join(COLOR_ATTRIBUTES) + r")\s*=\s*([\"'])(.*?)\2",
    re.DOTALL | re.IGNORECASE,
)
_STYLE_ATTR_RE = re.compile(r"(?<=\s)style\s*=\s*([\"'])(.*?)\1", re.DOTALL | re.IGNORECASE)


def _inside(pos: int, ranges: Sequence[tuple[int, int]]) -> bool:
    return any(lo <= pos < hi for lo, hi in ranges)


def find_svg_colors(svg_text: str) -> list[ColorToken]:
    """Every color in the document's attributes, style attributes and <style> elements."""
    scan = _COMMENT_RE.sub(lambda m: " " * len(m.group()), svg_text)
    tokens: list[ColorToken] = []

    style_ranges = []
    for m in _STYLE_ELEMENT_RE.finditer(scan):
        style_ranges.append((m.start(), m.end()))
        css = svg_text[m.start(1) : m.end(1)]
        css = css.replace("<![CDATA[", " " * 9).replace("]]>", " " * 3)
        tokens.extend(scan_css(css, base=m.start(1)))

    for m in _ATTR_RE.finditer(scan):
        if _inside(m.start(), style_ranges):
            continue
        raw = svg_text[m.start(3) : m.end(3)]
        value = raw.strip()
        parsed = parse_css_color(value)
        if parsed is None:  # none, url(#id), currentColor, inherit, ...
            continue
        start = m.start(3) + len(raw) - len(raw.lstrip())
        tokens.append(
            ColorToken(
                start=start,
                end=start + len(value),
                text=value,
                rgb=parsed[0],
                alpha=parsed[1],
                prop=m.group(1).lower(),
            )
        )

    for m in _STYLE_ATTR_RE.finditer(scan):
        if _inside(m.start(), style_ranges):
            continue
        # Scan the declarations as if they were the body of a rule
        body = "{" + svg_text[m.start(2) : m.end(2)] + "}"
        for t in scan_css(body, base=m.start(2) - 1):
            tokens.append(ColorToken(t.start, t.end, t.text, t.rgb, t.alpha, t.prop, None, None))

    return sorted(tokens, key=lambda t: t.start)


def svg_retheme(source: Source, theme: Theme | None = None, match: str = "order") -> str:
    """
    Rethemes an SVG (a path or file-like object) and returns the new markup.

    theme: a theme name, palette file, color list, or sequence of colors
           (default "Tropical")
    match: "order" gives the most-used colors the first palette colors,
           "luminance" pairs dark with dark and light with light
    """
    text = read_source(source)
    palette = theme if theme is not None else DEFAULT_THEME
    return recolor_tokens(text, find_svg_colors(text), palette, match=match).text
