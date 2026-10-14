import json

import pytest

from superwand.themes import (
    all_themes,
    color_themes,
    find_theme,
    match_palette,
    resolve_theme,
    theme_label,
    themes_dir,
    user_themes,
)


def test_builtin_themes_are_well_formed():
    assert len(color_themes) == 18
    for colors in color_themes.values():
        assert len(colors) == 8
        assert all(len(c) == 3 and all(0 <= v <= 255 for v in c) for c in colors)


def test_lookup_ignores_case_and_accents():
    assert find_theme("neon")[0] == "Neon"
    assert find_theme("PAIXAO")[0] == "Paixão"
    assert find_theme("nope") is None


def test_resolve_theme_forms(tmp_path):
    assert resolve_theme("Neon") == color_themes["Neon"]
    assert resolve_theme("#f00, navy") == [(255, 0, 0), (0, 0, 128)]
    assert resolve_theme([(1, 2, 3), "#fff"]) == [(1, 2, 3), (255, 255, 255)]
    path = tmp_path / "brand.json"
    path.write_text(json.dumps({"name": "Brand", "colors": ["#123456"]}))
    assert resolve_theme(str(path)) == [(18, 52, 86)]
    assert theme_label(str(path)) == "Brand"
    assert theme_label("neon") == "Neon"
    assert theme_label([(1, 2, 3)]) == "custom"


def test_unknown_theme_lists_choices():
    with pytest.raises(ValueError, match=r"Unknown theme 'Nope'.*Neon"):
        resolve_theme("Nope")


def test_user_themes(isolated_user_themes):
    assert themes_dir() == isolated_user_themes
    assert user_themes() == {}
    isolated_user_themes.mkdir()
    (isolated_user_themes / "mine.hex").write_text("#ff0000\n#00ff00\n")
    (isolated_user_themes / "Neon.json").write_text('["#000000"]')  # overrides the built-in
    (isolated_user_themes / "notes.md").write_text("ignored")
    (isolated_user_themes / "broken.json").write_text("{")
    with pytest.warns(UserWarning, match="broken.json"):
        themes = all_themes()
    assert themes["mine"] == [(255, 0, 0), (0, 255, 0)]
    assert themes["Neon"] == [(0, 0, 0)]
    with pytest.warns(UserWarning):
        assert resolve_theme("MINE") == [(255, 0, 0), (0, 255, 0)]


def test_themes_dir_defaults(monkeypatch, tmp_path):
    monkeypatch.delenv("SUPERWAND_THEMES_DIR")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr("sys.platform", "linux")
    assert themes_dir() == tmp_path / "superwand" / "themes"


def test_match_palette_order_cycles():
    regions = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    assert match_palette(regions, [(9, 9, 9), (8, 8, 8)]) == [(9, 9, 9), (8, 8, 8), (9, 9, 9)]


def test_match_palette_luminance_pairs_dark_with_dark():
    regions = [(250, 250, 250), (10, 10, 10), (120, 120, 120)]
    palette = [(0, 0, 128), (255, 255, 200), (100, 200, 100)]
    assert match_palette(regions, palette, match="luminance") == [
        (255, 255, 200),
        (0, 0, 128),
        (100, 200, 100),
    ]


@pytest.mark.parametrize(("palette", "match"), [([(1, 1, 1)], "nope"), ([], "order")])
def test_match_palette_rejects(palette, match):
    with pytest.raises(ValueError):
        match_palette([(0, 0, 0)], palette, match=match)
