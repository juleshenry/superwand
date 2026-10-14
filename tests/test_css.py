import io

import pytest

from superwand.color import contrast_ratio, parse_css_color
from superwand.css import (
    ContrastFix,
    ContrastIssue,
    check_contrast,
    css_retheme,
    find_colors,
    format_like,
    recolor_text,
)
from superwand.themes import color_themes

ONE = [(1, 2, 3)]

LEGACY_CSS = """  #fade, a:hover #abc {
    color:#fff;
    border: 1px solid #000; background: rgba(255, 0, 0, .5);
  }
  /* keep #123456 */
  .x { box-shadow: 0 0 2px #11223380 }
"""


def recolor(css: str, palette=ONE, **kwargs) -> str:
    return recolor_text(css, palette, **kwargs).text


def test_selectors_comments_indentation_and_alpha_are_preserved():
    out = css_retheme(io.StringIO(LEGACY_CSS), custom_theme=ONE)
    assert "#fade, a:hover #abc {" in out
    assert "color:#010203;" in out
    assert "1px solid #010203;" in out
    assert "rgba(1, 2, 3, .5)" in out
    assert "#01020380" in out
    assert "/* keep #123456 */" in out
    assert "    color:" in out


def test_css_without_colors_is_unchanged():
    css = "a { display: block; }"
    assert css_retheme(io.StringIO(css), "Neon") == css


def test_every_color_on_a_line_is_replaced():
    out = recolor("a { border: 1px solid #f00; outline: 2px dashed #0f0; color: #00f }")
    assert out == "a { border: 1px solid #010203; outline: 2px dashed #010203; color: #010203 }"


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("#abc", "#010203"),
        ("#ABC", "#010203"),  # no letters left to keep uppercase
        ("#ABCDEF", "#010203"),
        ("#abcd", "#010203dd"),
        ("#AbCdEf80", "#01020380"),
        ("rgb(255, 0, 0)", "rgb(1, 2, 3)"),
        ("rgba(255, 0, 0, .5)", "rgba(1, 2, 3, .5)"),
        ("rgb(255 0 0)", "rgb(1 2 3)"),
        ("rgb(255 0 0 / 50%)", "rgb(1 2 3 / 50%)"),
        ("RGB(100%, 0%, 0%)", "RGB(0.39%, 0.78%, 1.18%)"),
        ("red", "#010203"),
        ("Tomato", "#010203"),
    ],
)
def test_format_is_preserved(original, expected):
    assert recolor(f"a {{ color: {original}; }}") == f"a {{ color: {expected}; }}"


def test_uppercase_hex_stays_uppercase():
    out = recolor("a { color: #FFF; }", [(171, 205, 239)])
    assert out == "a { color: #ABCDEF; }"


def test_hsl_keeps_notation_units_and_alpha():
    out = recolor(
        "a { color: hsl(120, 100%, 25%); background: hsla(120deg 100% 25% / .3); "
        "border-color: hsl(0.5turn 50% 50%) }",
        [(255, 0, 0)],
    )
    assert "color: hsl(0, 100%, 50%);" in out
    assert "hsla(0deg 100% 50% / .3)" in out
    assert "hsl(0turn 100% 50%)" in out


def test_oklch_and_oklab_keep_notation():
    out = recolor(
        "a { color: oklch(62.8% 0.2577 29.23); background: oklab(0.5 0.1 -0.1 / 0.4) }",
        [(0, 0, 255)],
    )
    oklch = out[out.index("oklch(") : out.index(")") + 1]
    assert oklch.split()[0].endswith("%")
    rgb, alpha = parse_css_color(oklch)
    assert alpha is None
    assert all(abs(a - b) <= 1 for a, b in zip(rgb, (0, 0, 255), strict=False))
    oklab = out[out.index("oklab(") : out.rindex(")") + 1]
    assert oklab.endswith(" / 0.4)") and "%" not in oklab
    rgb, alpha = parse_css_color(oklab)
    assert alpha == "0.4"
    assert all(abs(a - b) <= 1 for a, b in zip(rgb, (0, 0, 255), strict=False))


def test_named_colors_only_in_color_properties():
    css = (
        "p { color: red; background: white url(red.png); font-family: Tan; "
        'content: "red #fff"; animation-name: navy; grid-area: teal; }'
    )
    out = recolor(css)
    assert "color: #010203;" in out
    assert "background: #010203 url(red.png);" in out
    assert "font-family: Tan;" in out
    assert 'content: "red #fff";' in out
    assert "animation-name: navy;" in out
    assert "grid-area: teal;" in out


def test_keywords_and_variables_are_left_alone():
    css = (
        "a { color: currentColor; background: transparent; "
        "border-color: inherit; fill: var(--red); }"
    )
    assert recolor(css) == css


def test_class_and_id_names_are_not_colors():
    css = ".red, #blue > .tan { box-shadow: 0 0 1px black; }"
    assert recolor(css) == ".red, #blue > .tan { box-shadow: 0 0 1px #010203; }"


def test_url_fragments_and_strings_are_ignored():
    css = 'a { background: url(#fade) #fff; mask: url("img.svg#abc"); content: "#fff"; }'
    out = recolor(css)
    assert out == 'a { background: url(#fade) #010203; mask: url("img.svg#abc"); content: "#fff"; }'


def test_media_query_prelude_is_not_touched():
    css = "@media (prefers-color-scheme: dark) { body { color: #fff } }"
    assert recolor(css) == "@media (prefers-color-scheme: dark) { body { color: #010203 } }"


def test_custom_properties():
    css = ":root { --brand: #ff0000; --accent: tomato; --size: 4px; }"
    assert recolor(css) == ":root { --brand: #010203; --accent: #010203; --size: 4px; }"


def test_find_colors_reports_property_and_selector():
    css = "a:hover, .btn { color: #fff; }\n@media print { body { background: black } }"
    tokens = find_colors(css)
    assert [(t.text, t.prop, t.selector) for t in tokens] == [
        ("#fff", "color", "a:hover, .btn"),
        ("black", "background", "body"),
    ]
    assert css[tokens[0].start : tokens[0].end] == "#fff"
    assert tokens[0].rgb == (255, 255, 255)


def test_clusters_map_to_palette_colors_only():
    css = (
        "a { color: #f00; } b { color: #e00; } c { color: #00f; } "
        "d { color: #00e; } e { color: #0f0 }"
    )
    palette = [(10, 10, 10), (200, 200, 200)]
    out = recolor(css, palette)
    found = {t.rgb for t in find_colors(out)}
    assert found <= set(palette)
    # Similar reds land in the same cluster
    assert len({t.rgb for t in find_colors(out)[:2]}) == 1


def test_most_used_cluster_gets_first_color():
    css = "a { color: #f00 } b { color: #f00 } c { color: #f00 } d { color: #00f }"
    out = recolor(css, [(1, 1, 1), (2, 2, 2)])
    assert out.count("#010101") == 3
    assert out.count("#020202") == 1


def test_luminance_match_pairs_dark_with_dark():
    css = "a { color: #000; background: #fff }"
    out = recolor(css, [(250, 250, 200), (20, 20, 60)], match="luminance")
    assert out == "a { color: #14143c; background: #fafac8 }"


def test_bad_match_mode():
    with pytest.raises(ValueError, match="match must be one of"):
        recolor("a { color: red }", match="nope")


def test_bad_kind():
    with pytest.raises(ValueError, match="kind"):
        recolor_text("a { color: red }", ONE, kind="html")


def test_theme_forms(tmp_path):
    css = "a { color: #123456 }"
    first_neon = "#{:02x}{:02x}{:02x}".format(*color_themes["Neon"][0])
    assert first_neon in css_retheme(io.StringIO(css), "Neon")
    assert first_neon in css_retheme(io.StringIO(css), "neon")
    assert "#ff0080" in css_retheme(io.StringIO(css), "#ff0080,#00ffff")
    assert "#00ffff" in css_retheme(io.StringIO(css), [(0, 255, 255)])
    with pytest.raises(ValueError, match="Unknown theme"):
        css_retheme(io.StringIO(css), "NotATheme")


def test_default_theme_is_tropical():
    first = "#{:02x}{:02x}{:02x}".format(*color_themes["Tropical"][0])
    assert first in css_retheme(io.StringIO("a { color: #123456 }"))


def test_custom_theme_wins_over_theme():
    assert "#010203" in css_retheme(io.StringIO("a { color: red }"), "Neon", custom_theme=ONE)


def test_empty_custom_theme_falls_back_to_theme():
    out = css_retheme(io.StringIO("a { color: red }"), [(4, 5, 6)], custom_theme=[])
    assert "#040506" in out


def test_path_and_bytes_inputs(tmp_path):
    path = tmp_path / "site.css"
    path.write_text("a { color: red }", encoding="utf-8")
    assert css_retheme(path, ONE) == "a { color: #010203 }"
    assert css_retheme(str(path), ONE) == "a { color: #010203 }"
    stream = io.BytesIO(b"a { color: red }")
    assert css_retheme(stream, ONE) == "a { color: #010203 }"
    assert stream.read() == b"a { color: red }"  # rewound for the caller


def test_check_contrast_finds_low_pairs():
    css = "p { color: #777; background: #888 } a { color: #000; background-color: #fff }"
    issues = check_contrast(css)
    assert len(issues) == 1
    issue = issues[0]
    assert isinstance(issue, ContrastIssue)
    assert (issue.selector, issue.fg, issue.bg) == ("p", (119, 119, 119), (136, 136, 136))
    assert issue.ratio == pytest.approx(contrast_ratio((119, 119, 119), (136, 136, 136)))
    assert check_contrast(css, min_contrast=1.1) == []


def test_min_contrast_fixes_text_color():
    css = "p { color: #777; background: #888 }"
    palette = [(200, 200, 200), (210, 210, 210)]
    plain = recolor_text(css, palette)
    assert plain.contrast_fixes == []
    fixed = recolor_text(css, palette, min_contrast=4.5)
    assert len(fixed.contrast_fixes) == 1
    fix = fixed.contrast_fixes[0]
    assert isinstance(fix, ContrastFix)
    assert fix.selector == "p"
    assert fix.ratio_before < 4.5 <= fix.ratio_after
    assert check_contrast(fixed.text, 4.5) == []
    # Only the text color moves; the background keeps its palette color
    assert "background: #d2d2d2" in fixed.text or "background: #c8c8c8" in fixed.text


def test_min_contrast_uses_last_background_and_leaves_good_pairs():
    css = "p { color: #000; background: #000; background: #fff }"
    fixed = recolor_text(css, [(0, 0, 0), (255, 255, 255)], min_contrast=4.5)
    assert fixed.contrast_fixes == []


def test_css_retheme_min_contrast():
    css = "p { color: #777; background: #888 }"
    out = css_retheme(io.StringIO(css), [(200, 200, 200)], min_contrast=4.5)
    assert check_contrast(out, 4.5) == []


def test_format_like_named_and_unknown_alpha():
    assert format_like("navy", (1, 2, 3), None) == "#010203"
    assert format_like("rgba(0,0,0,50%)", (1, 2, 3), "50%") == "rgba(1, 2, 3, 50%)"


def test_nested_blocks_pair_by_innermost_rule():
    css = ".a { color: #fff; .b { background: #fff } }"
    tokens = find_colors(css)
    assert tokens[0].block != tokens[1].block
    assert check_contrast(css) == []
