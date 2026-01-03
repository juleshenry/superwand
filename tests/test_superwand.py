import pytest
from superwand.superwand import clamp, SuperWand
from superwand import __color_themes__


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_superwand_init():
    sw = SuperWand(__color_themes__.color_themes, 8)
    assert sw.color_themes == __color_themes__.color_themes
    assert sw.number == 8


# Note: apply_theme_to_image modifies files, so for full test, use tmp_path
def test_apply_theme_to_image(tmp_path):
    # This is a placeholder; actual test would require image files and check output
    # For now, just ensure no exception on init
    sw = SuperWand(__color_themes__.color_themes, 8)
    # sw.apply_theme_to_image("nonexistent.png", "Tropical")  # Would raise if file not found
    pass
