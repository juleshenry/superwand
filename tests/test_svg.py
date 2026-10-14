import io

import pytest

from superwand.css import recolor_text
from superwand.svg import find_svg_colors, svg_retheme
from superwand.themes import color_themes

ONE = [(1, 2, 3)]

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <!-- fill="#123456" stroke='red' -->
  <style><![CDATA[
    .a { fill: red; stroke: #00f }
  ]]></style>
  <defs>
    <linearGradient id="fade">
      <stop offset="0" stop-color="#ff000080"/>
      <stop offset="1" stop-color='blue'/>
    </linearGradient>
  </defs>
  <rect id="abc" fill="url(#fade)" stroke="none" color="currentColor"/>
  <path fill = " #00ff00 " style="fill:#00ff00; stroke-width:2;stroke:navy"/>
  <circle class="a" fill="inherit" flood-color="rgb(10, 20, 30)"/>
</svg>
"""


def test_finds_attributes_style_attributes_and_style_elements():
    found = [(t.text, t.prop) for t in find_svg_colors(SVG)]
    assert found == [
        ("red", "fill"),
        ("#00f", "stroke"),
        ("#ff000080", "stop-color"),
        ("blue", "stop-color"),
        ("#00ff00", "fill"),
        ("#00ff00", "fill"),
        ("navy", "stroke"),
        ("rgb(10, 20, 30)", "flood-color"),
    ]
    for t in find_svg_colors(SVG):
        assert SVG[t.start : t.end] == t.text


def test_svg_retheme_replaces_only_colors():
    out = svg_retheme(io.StringIO(SVG), ONE)
    assert "<!-- fill=\"#123456\" stroke='red' -->" in out
    assert ".a { fill: #010203; stroke: #010203 }" in out
    assert 'stop-color="#01020380"' in out
    assert "stop-color='#010203'" in out
    assert '<rect id="abc" fill="url(#fade)" stroke="none" color="currentColor"/>' in out
    assert 'fill = " #010203 "' in out
    assert 'style="fill:#010203; stroke-width:2;stroke:#010203"' in out
    assert 'fill="inherit" flood-color="rgb(1, 2, 3)"' in out
    assert 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"' in out
    assert "<![CDATA[" in out and "]]>" in out


def test_svg_without_colors_is_unchanged():
    svg = '<svg><rect fill="none" stroke="url(#g)"/></svg>'
    assert svg_retheme(io.StringIO(svg), "Neon") == svg


def test_color_attribute_suffixes_are_not_confused():
    svg = '<svg><stop stop-color="#fff"/><filter flood-color="#000"/></svg>'
    assert [t.prop for t in find_svg_colors(svg)] == ["stop-color", "flood-color"]


def test_names_and_ids_are_not_colors():
    svg = '<svg><g id="red" class="tan"><text font-family="Tan">red</text></g></svg>'
    assert find_svg_colors(svg) == []


def test_recolor_text_svg_kind_matches_svg_retheme():
    assert recolor_text(SVG, ONE, kind="svg").text == svg_retheme(io.StringIO(SVG), ONE)


def test_path_input_and_theme_name(tmp_path):
    path = tmp_path / "logo.svg"
    path.write_text('<svg><rect fill="#123456"/></svg>', encoding="utf-8")
    first = "#{:02x}{:02x}{:02x}".format(*color_themes["Volcano"][0])
    assert svg_retheme(path, "Volcano") == f'<svg><rect fill="{first}"/></svg>'
    assert svg_retheme(str(path), ONE) == '<svg><rect fill="#010203"/></svg>'


def test_default_theme_is_tropical():
    first = "#{:02x}{:02x}{:02x}".format(*color_themes["Tropical"][0])
    assert svg_retheme(io.StringIO('<svg fill="#123"/>')) == f'<svg fill="{first}"/>'


def test_luminance_match():
    svg = '<svg><rect fill="#000"/><rect fill="#fff"/></svg>'
    out = svg_retheme(io.StringIO(svg), [(250, 250, 200), (20, 20, 60)], match="luminance")
    assert out == '<svg><rect fill="#14143c"/><rect fill="#fafac8"/></svg>'


def test_bad_theme():
    with pytest.raises(ValueError, match="Unknown theme"):
        svg_retheme(io.StringIO('<svg fill="red"/>'), "NotATheme")
