import json

import pytest

from superwand.palette_io import FORMATS, dumps_palette, load_palette, save_palette

COLORS = [(255, 0, 128), (0, 255, 255), (26, 0, 51)]


@pytest.mark.parametrize("ext", [".hex", ".json", ".css", ".gpl", ".ase"])
def test_round_trip(tmp_path, ext):
    path = save_palette(COLORS, tmp_path / f"brand{ext}", name="Brand")
    name, colors = load_palette(path)
    assert colors == COLORS
    assert name == ("Brand" if ext in (".json", ".gpl", ".ase") else "brand")


def test_explicit_format_overrides_extension(tmp_path):
    path = save_palette(COLORS, tmp_path / "x.txt", fmt="json")
    assert json.loads(path.read_text())["colors"][0] == "#ff0080"


def test_dumps_formats():
    assert dumps_palette(COLORS, "hex") == "#ff0080\n#00ffff\n#1a0033\n"
    assert "--my-theme-1: #ff0080;" in dumps_palette(COLORS, "css", "My Theme")
    assert dumps_palette(COLORS, "gpl").startswith("GIMP Palette\nName: superwand\n")
    assert dumps_palette(COLORS, "ase")[:4] == b"ASEF"
    assert set(FORMATS) == {"hex", "json", "css", "gpl", "ase"}
    with pytest.raises(ValueError):
        dumps_palette(COLORS, "pdf")


def test_load_hex_skips_comments(tmp_path):
    path = tmp_path / "lospec.txt"
    path.write_text("; paint.net palette\n# comment\n// note\nff0080\n#00ffff 1a0033\n\n")
    assert load_palette(path)[1] == COLORS


def test_load_toml(tmp_path):
    path = tmp_path / "t.toml"
    path.write_text('name = "Toml Theme"\ncolors = ["#ff0080", [0, 255, 255]]\n')
    assert load_palette(path) == ("Toml Theme", COLORS[:2])


def test_load_json_list_and_css_variables(tmp_path):
    (tmp_path / "a.json").write_text('["#ff0080", "aqua"]')
    assert load_palette(tmp_path / "a.json")[1] == COLORS[:2]
    (tmp_path / "vars.css").write_text(":root { --a: #ff0080; --b: rgb(0 255 255); }")
    assert load_palette(tmp_path / "vars.css")[1] == COLORS[:2]


@pytest.mark.parametrize(
    ("ext", "content"),
    [(".gpl", "not a palette"), (".hex", "; only comments\n"), (".ase", "nope")],
)
def test_load_rejects_bad_files(tmp_path, ext, content):
    path = tmp_path / f"bad{ext}"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_palette(path)
