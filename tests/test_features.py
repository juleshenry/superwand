import io
import sys
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

from superwand import (
    color_themes,
    css_retheme,
    extract_palette,
    gradient_enforce,
    np_get_prominent_regions,
    retheme,
    theme_cycle_gif,
    transfer_palette,
)
from superwand.core.np_region_identifier import match_palette
from superwand.utils.gif_maker import inv


@pytest.fixture
def quad_img():
    """Four flat quadrants: black, dark gray, light gray, white (largest first)."""
    arr = np.zeros((40, 40, 3), dtype=np.uint8)
    arr[:, :] = (0, 0, 0)
    arr[:20, 20:] = (80, 80, 80)
    arr[20:, :20] = (170, 170, 170)
    arr[30:, 30:] = (250, 250, 250)
    return Image.fromarray(arr)


def test_match_palette_order_cycles():
    regions = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    assert match_palette(regions, [(9, 9, 9), (8, 8, 8)]) == [
        (9, 9, 9),
        (8, 8, 8),
        (9, 9, 9),
    ]


def test_match_palette_luminance_pairs_dark_with_dark():
    regions = [(250, 250, 250), (10, 10, 10), (120, 120, 120)]
    palette = [(0, 0, 128), (255, 255, 200), (100, 200, 100)]
    assigned = match_palette(regions, palette, match="luminance")
    assert assigned == [(255, 255, 200), (0, 0, 128), (100, 200, 100)]


def test_match_palette_rejects_bad_mode():
    with pytest.raises(ValueError):
        match_palette([(0, 0, 0)], [(1, 1, 1)], match="nope")


def test_regions_are_deterministic(quad_img):
    a = np_get_prominent_regions(quad_img, number=4)
    b = np_get_prominent_regions(quad_img, number=4)
    assert list(a.keys()) == list(b.keys())


def test_retheme_returns_image_with_theme_colors(quad_img):
    out = retheme(quad_img, "Neon", k=4)
    assert out.size == quad_img.size
    used = {tuple(c) for c in np.array(out)[..., :3].reshape(-1, 3)}
    assert used <= set(color_themes["Neon"][:4])


def test_retheme_accepts_custom_palette(quad_img):
    palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    out = retheme(quad_img, palette, k=4)
    assert np.array(out)[0, 0, :3].tolist() == [255, 0, 0]  # largest region


def test_retheme_unknown_theme(quad_img):
    with pytest.raises(ValueError, match="Unknown theme"):
        retheme(quad_img, "NotATheme")


def test_transfer_palette_luminance(quad_img):
    ref = Image.new("RGB", (10, 10), (200, 30, 30))
    ref.paste((20, 20, 90), (0, 0, 5, 10))
    out = np.array(transfer_palette(quad_img, ref, k=2))
    # The black quadrant is darkest, so it takes the reference's dark blue
    assert out[0, 0, :3].tolist() == [20, 20, 90]


def test_extract_palette(quad_img):
    palette = extract_palette(quad_img, 4)
    assert len(palette) == 4
    assert palette[0] == (0, 0, 0)


def test_gradient_enforce_makes_gradient(quad_img):
    out = np.array(gradient_enforce(quad_img, style="top-down", number=4))
    column = out[:20, 25, 0]  # dark gray quadrant, top half
    assert column[0] > column[-1]


def test_theme_cycle_gif(tmp_path, quad_img):
    path = tmp_path / "cycle.gif"
    theme_cycle_gif(quad_img, str(path), themes=["Neon", "Arctic", "Volcano"], k=4)
    with Image.open(path) as gif:
        assert gif.n_frames == 3


def test_inv_inverts_channels_not_columns():
    img = Image.fromarray(np.full((4, 6, 3), 10, dtype=np.uint8))
    assert (np.array(inv(img)) == 245).all()


CSS = """  #fade, a:hover #abc {
    color:#fff;
    border: 1px solid #000; background: rgba(255, 0, 0, .5);
  }
  /* keep #123456 */
  .x { box-shadow: 0 0 2px #11223380 }
"""


def test_css_three_digit_hex_and_selectors():
    out = css_retheme(io.StringIO(CSS), custom_theme=[(1, 2, 3)])
    assert "#fade, a:hover #abc {" in out
    assert "color:#010203;" in out
    assert "1px solid #010203;" in out
    assert "rgba(1, 2, 3, .5)" in out
    assert "#01020380" in out  # alpha preserved
    assert "/* keep #123456 */" in out
    assert "    color:" in out  # indentation preserved


def test_css_without_colors_is_unchanged():
    css = "a { display: block; }"
    assert css_retheme(io.StringIO(css), "Neon") == css


def test_cli_list_themes(capsys):
    from superwand.core.superwand import main

    with patch.object(sys, "argv", ["superwand", "--list-themes"]):
        main()
    out = capsys.readouterr().out
    assert all(name in out for name in color_themes)


def test_cli_output_dir_and_palette_from(tmp_path, quad_img):
    from superwand.core.superwand import main

    src, ref = tmp_path / "quad.png", tmp_path / "ref.png"
    quad_img.save(src)
    Image.new("RGB", (8, 8), (200, 30, 30)).save(ref)
    out_dir = tmp_path / "out"

    argv = ["superwand", str(src), "-theme", "Urban", "-o", str(out_dir)]
    with patch.object(sys, "argv", argv):
        main()
    assert (out_dir / "quad_Urban.png").exists()

    argv = ["superwand", str(src), "-palette-from", str(ref), "-k", "1", "-o", str(out_dir)]
    with patch.object(sys, "argv", argv):
        main()
    assert (out_dir / "quad_from_ref.png").exists()
