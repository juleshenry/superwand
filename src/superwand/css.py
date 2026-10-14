"""
Retheme the colors in a stylesheet.

Every color literal in a declaration value (hex, rgb()/rgba(), hsl()/hsla(),
oklch(), oklab() and named colors in color properties) is clustered in OKLab,
weighted by how often it is used, and each cluster is mapped to a palette
color. Selectors, comments, strings, url()s, formatting and alpha channels are
left untouched, and each color keeps the notation it was written in.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import IO

import numpy as np
from sklearn.cluster import KMeans

from ._named_colors import NAMED_COLORS
from .color import (
    RGB,
    contrast_ratio,
    ensure_contrast,
    oklab_to_oklch,
    oklab_to_rgb,
    parse_css_color,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_oklab,
    split_args,
    srgb_to_oklab,
)
from .themes import MATCH_MODES, Theme, match_palette, resolve_theme

Source = str | PathLike[str] | IO[str] | IO[bytes]

DEFAULT_THEME = "Tropical"

# Candidate color literals: hex, color functions, and bare words (named colors)
TOKEN_RE = re.compile(
    r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])"
    r"|\b(?:rgba?|hsla?|oklch|oklab)\([^()]*\)"
    r"|(?<![\w#.@$%-])[a-zA-Z]+(?![\w(%-])",
    re.IGNORECASE,
)
# Comments, strings and url()s never hold colors to recolor; blanked before scanning
_OPAQUE_RE = re.compile(
    r"/\*.*?\*/"
    r"|\"(?:\\.|[^\"\\])*\""
    r"|'(?:\\.|[^'\\])*'"
    r"|\burl\((?:[^()'\"]|\"[^\"]*\"|'[^']*')*\)",
    re.DOTALL | re.IGNORECASE,
)
_COLOR_PROPS = {
    "color",
    "fill",
    "stroke",
    "caret-color",
    "accent-color",
    "stop-color",
    "flood-color",
    "lighting-color",
}
_COLOR_PROP_PREFIXES = ("background", "border", "outline", "column-rule", "scrollbar")
_COLOR_PROP_PARTS = ("shadow", "decoration")
_BACKGROUND_PROPS = ("background", "background-color")


@dataclass(frozen=True)
class ColorToken:
    """One color literal: its span in the source text, value, and where it sits."""

    start: int
    end: int
    text: str
    rgb: RGB
    alpha: str | None
    prop: str | None = None
    block: int | None = None
    selector: str | None = None


@dataclass(frozen=True)
class ContrastIssue:
    """A text/background pair in one rule whose contrast is below the minimum."""

    selector: str
    fg: RGB
    bg: RGB
    ratio: float


@dataclass(frozen=True)
class ContrastFix:
    """A text color that recolor_text adjusted to keep it readable on its background."""

    selector: str
    before: RGB
    after: RGB
    background: RGB
    ratio_before: float
    ratio_after: float


@dataclass
class Recolored:
    """The rethemed text plus any contrast adjustments that were made."""

    text: str
    contrast_fixes: list[ContrastFix] = field(default_factory=list)


def read_source(source: Source) -> str:
    """Reads a path or a text/bytes file-like object (rewinding it afterwards)."""
    if hasattr(source, "read"):
        content = source.read()
        if hasattr(source, "seek"):
            source.seek(0)
        return content.decode("utf-8") if isinstance(content, bytes) else content
    return Path(source).read_text(encoding="utf-8")


def blank_opaque(text: str) -> str:
    """Replaces comments, strings and url()s with spaces, keeping every offset."""
    return _OPAQUE_RE.sub(lambda m: " " * len(m.group()), text)


def is_color_property(prop: str) -> bool:
    """True if named colors in this property's value should be recolored."""
    return (
        prop.startswith("--")
        or prop in _COLOR_PROPS
        or prop.endswith("color")
        or prop.startswith(_COLOR_PROP_PREFIXES)
        or any(part in prop for part in _COLOR_PROP_PARTS)
    )


def _declaration_property(scan: str, start: int, end: int) -> str | None:
    """
    The property name if scan[start:end] sits in a declaration value
    (`prop: <here>;`), or None for selectors, at-rule preludes and the like.
    """
    before = max(scan.rfind(c, 0, start) for c in "{};")
    if before == -1 or scan[before] == "}":
        return None
    head = scan[before + 1 : start]
    if ":" not in head:
        return None
    after = [i for i in (scan.find(c, end) for c in "{};") if i != -1]
    if after and scan[min(after)] == "{":
        return None
    return head.split(":", 1)[0].strip().lower()


def _block_owners(scan: str, positions: Iterable[int]) -> dict[int, int | None]:
    """Maps each position to the offset of the `{` of its innermost enclosing block."""
    events = [(m.start(), m.group()) for m in re.finditer(r"[{}]", scan)]
    owners: dict[int, int | None] = {}
    stack: list[int] = []
    i = 0
    for pos in sorted(positions):
        while i < len(events) and events[i][0] < pos:
            offset, brace = events[i]
            if brace == "{":
                stack.append(offset)
            elif stack:
                stack.pop()
            i += 1
        owners[pos] = stack[-1] if stack else None
    return owners


def _selector(scan: str, block: int) -> str:
    """The prelude before the `{` at `block`, e.g. 'a:hover, .btn'."""
    prev = max(scan.rfind(c, 0, block) for c in "{};")
    return " ".join(scan[prev + 1 : block].split())


def scan_css(text: str, base: int = 0) -> list[ColorToken]:
    """
    Finds the color literals in CSS `text`. Offsets (and block ids) are shifted
    by `base`, so callers can scan a slice of a larger document.
    """
    scan = blank_opaque(text)
    candidates: list[tuple[int, int, str, RGB, str | None, str]] = []
    for m in TOKEN_RE.finditer(scan):
        literal = m.group()
        is_word = literal.isalpha()
        if is_word and literal.lower() not in NAMED_COLORS:
            continue
        prop = _declaration_property(scan, m.start(), m.end())
        if prop is None or (is_word and not is_color_property(prop)):
            continue
        parsed = parse_css_color(text[m.start() : m.end()])
        if parsed is None:
            continue
        candidates.append((m.start(), m.end(), text[m.start() : m.end()], *parsed, prop))

    owners = _block_owners(scan, (c[0] for c in candidates))
    selectors: dict[int, str] = {}
    tokens = []
    for start, end, literal, rgb, alpha, prop in candidates:
        block = owners[start]
        selector = None
        if block is not None:
            if block not in selectors:
                selectors[block] = _selector(scan, block)
            selector = selectors[block]
        tokens.append(
            ColorToken(
                start=start + base,
                end=end + base,
                text=literal,
                rgb=rgb,
                alpha=alpha,
                prop=prop,
                block=None if block is None else block + base,
                selector=selector,
            )
        )
    return tokens


def find_colors(css_text: str) -> list[ColorToken]:
    """Every color literal in a declaration value of the stylesheet, in order."""
    return scan_css(css_text)


# --- formatting ----------------------------------------------------------------


def _fmt(x: float, digits: int) -> str:
    out = f"{x:.{digits}f}"
    if "." in out:
        out = out.rstrip("0").rstrip(".")
    return "0" if out in ("", "-0") else out


_ANGLE_UNITS = {"deg": 1.0, "grad": 0.9, "turn": 360.0, "rad": 57.29577951308232}


def _hue(degrees: float, original: str) -> str:
    """A hue in the unit the original component used."""
    lowered = original.strip().lower()
    for unit in ("grad", "turn", "rad", "deg"):
        if lowered.endswith(unit):
            digits = 4 if unit in ("turn", "rad") else 2
            return _fmt(degrees / _ANGLE_UNITS[unit], digits) + unit
    return _fmt(degrees, 2)


def _scaled(value: float, original: str, percent_of: float, digits: int) -> str:
    """A component written as a percentage if the original was one."""
    if original.strip().endswith("%"):
        return _fmt(value / percent_of * 100, 2) + "%"
    return _fmt(value, digits)


def format_like(original: str, rgb: Sequence[int], alpha: str | None) -> str:
    """`rgb` written in the same notation as the literal `original`, with its alpha."""
    rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    if original.startswith("#"):
        digits = original[1:]
        out = rgb_to_hex(rgb)[1:] + (alpha or "")
        upper = digits == digits.upper() and any(c.isalpha() for c in digits)
        return "#" + (out.upper() if upper else out.lower())
    if "(" not in original:  # named color
        return rgb_to_hex(rgb)

    name = original[: original.index("(")]
    func = name.lower()
    inner = original[original.index("(") + 1 : -1]
    parts, _ = split_args(inner)
    parts = [*parts, "", "", ""][:3]

    if func.startswith("rgb"):
        comps = [_scaled(c, p, 255, 0) for c, p in zip(rgb, parts, strict=False)]
    elif func.startswith("hsl"):
        h, s, light = rgb_to_hsl(rgb)
        comps = [_hue(h, parts[0])]
        for value, p in ((s, parts[1]), (light, parts[2])):
            comps.append(_fmt(value * 100, 2) + ("%" if p.strip().endswith("%") else ""))
    elif func == "oklch":
        L, C, H = oklab_to_oklch(rgb_to_oklab(rgb))
        comps = [_scaled(L, parts[0], 1, 4), _scaled(C, parts[1], 0.4, 4), _hue(H, parts[2])]
    else:  # oklab
        L, a, b = rgb_to_oklab(rgb)
        comps = [
            _scaled(L, parts[0], 1, 4),
            _scaled(a, parts[1], 0.4, 4),
            _scaled(b, parts[2], 0.4, 4),
        ]

    if "," in inner and "/" not in inner:
        body = ", ".join(comps) + (f", {alpha}" if alpha is not None else "")
    else:
        body = " ".join(comps) + (f" / {alpha}" if alpha is not None else "")
    return f"{name}({body})"


# --- recoloring ----------------------------------------------------------------


def _cluster_mapping(
    tokens: Sequence[ColorToken], palette: list[RGB], match: str
) -> dict[RGB, RGB]:
    """Clusters the tokens' colors in OKLab and maps every color to a palette color."""
    usage = Counter(t.rgb for t in tokens)
    unique = list(usage)
    n_clusters = min(len(palette), len(unique))
    kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto").fit(
        srgb_to_oklab(np.array(unique, dtype=np.float64)),
        sample_weight=[usage[c] for c in unique],
    )
    labels = [int(label) for label in kmeans.labels_]

    # Most-used cluster first, so match="order" gives it the first palette color
    weight: Counter[int] = Counter()
    for color, label in zip(unique, labels, strict=False):
        weight[label] += usage[color]
    order = [label for label, _ in weight.most_common()]
    centers = [oklab_to_rgb(kmeans.cluster_centers_[label]) for label in order]
    assigned = dict(zip(order, match_palette(centers, palette, match), strict=False))
    return {color: assigned[label] for color, label in zip(unique, labels, strict=False)}


def _contrast_pairs(
    tokens: Sequence[ColorToken],
) -> Iterable[tuple[str, list[int], int]]:
    """Yields (selector, text color token indexes, background token index) per rule block."""
    blocks: dict[int, list[int]] = defaultdict(list)
    for i, t in enumerate(tokens):
        if t.block is not None:
            blocks[t.block].append(i)
    for indexes in blocks.values():
        fg = [i for i in indexes if tokens[i].prop == "color"]
        bg = [i for i in indexes if tokens[i].prop in _BACKGROUND_PROPS]
        if fg and bg:
            yield tokens[fg[0]].selector or "", fg, bg[-1]  # the last background wins


def recolor_tokens(
    text: str,
    tokens: Sequence[ColorToken],
    palette: Theme,
    *,
    match: str = "order",
    min_contrast: float | None = None,
) -> Recolored:
    """Replaces each token in `text` with its mapped palette color."""
    if match not in MATCH_MODES:
        raise ValueError(f"match must be one of {MATCH_MODES}, got {match!r}")
    colors = resolve_theme(palette)
    if not tokens:
        return Recolored(text)

    mapping = _cluster_mapping(tokens, colors, match)
    new = [mapping[t.rgb] for t in tokens]

    fixes: list[ContrastFix] = []
    if min_contrast:
        for selector, fg_indexes, bg_index in _contrast_pairs(tokens):
            background = new[bg_index]
            for i in fg_indexes:
                before = new[i]
                ratio = contrast_ratio(before, background)
                if ratio >= min_contrast:
                    continue
                after = ensure_contrast(before, background, min_contrast)
                new[i] = after
                fixes.append(
                    ContrastFix(
                        selector=selector,
                        before=before,
                        after=after,
                        background=background,
                        ratio_before=ratio,
                        ratio_after=contrast_ratio(after, background),
                    )
                )

    out, last = [], 0
    for token, rgb in sorted(zip(tokens, new, strict=False), key=lambda pair: pair[0].start):
        out.append(text[last : token.start])
        out.append(format_like(token.text, rgb, token.alpha))
        last = token.end
    out.append(text[last:])
    return Recolored("".join(out), fixes)


def recolor_text(
    text: str,
    palette: Theme,
    *,
    kind: str = "css",
    match: str = "order",
    min_contrast: float | None = None,
) -> Recolored:
    """
    Rethemes CSS (kind="css") or SVG (kind="svg") source text with `palette`.
    With `min_contrast`, text colors that end up too close to their rule's
    background are pushed lighter or darker until they reach that WCAG ratio.
    """
    if kind == "css":
        tokens = find_colors(text)
    elif kind == "svg":
        from .svg import find_svg_colors

        tokens = find_svg_colors(text)
    else:
        raise ValueError(f"kind must be 'css' or 'svg', got {kind!r}")
    return recolor_tokens(text, tokens, palette, match=match, min_contrast=min_contrast)


def css_retheme(
    source: Source,
    theme: Theme | None = None,
    custom_theme: Sequence[Sequence[int]] | None = None,
    match: str = "order",
    *,
    min_contrast: float | None = None,
) -> str:
    """
    Rethemes a stylesheet (a path or file-like object) and returns the new CSS.

    theme:        a theme name, palette file, color list, or sequence of colors
                  (default "Tropical")
    custom_theme: explicit colors; takes precedence over `theme`
    match:        "order" gives the most-used colors the first palette colors,
                  "luminance" pairs dark with dark and light with light
    min_contrast: if set (e.g. 4.5), fix text colors that would be unreadable
                  on the background of the same rule
    """
    palette: Theme = (
        custom_theme if custom_theme else (theme if theme is not None else DEFAULT_THEME)
    )
    return recolor_text(
        read_source(source), palette, kind="css", match=match, min_contrast=min_contrast
    ).text


def check_contrast(css_text: str, min_contrast: float = 4.5) -> list[ContrastIssue]:
    """Text/background pairs in the same rule whose contrast is below `min_contrast`."""
    tokens = find_colors(css_text)
    issues = []
    for selector, fg_indexes, bg_index in _contrast_pairs(tokens):
        bg = tokens[bg_index].rgb
        for i in fg_indexes:
            ratio = contrast_ratio(tokens[i].rgb, bg)
            if ratio < min_contrast:
                issues.append(ContrastIssue(selector, tokens[i].rgb, bg, ratio))
    return issues
