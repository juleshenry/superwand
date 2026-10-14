import numpy as np
import pytest
from PIL import Image

from superwand import color_themes, find_regions, gradient_enforce, retheme, transfer_palette
from superwand.color import lightness
from superwand.render import paint, retheme_file

PALETTE = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]


def colors_in(img):
    return {tuple(c) for c in np.array(img)[..., :3].reshape(-1, 3)}


def test_retheme_uses_theme_colors(quad_img):
    out = retheme(quad_img, "Neon", k=4)
    assert out.mode == "RGBA" and out.size == quad_img.size
    assert colors_in(out) <= set(color_themes["Neon"][:4])


def test_retheme_custom_palette_maps_largest_first(quad_img):
    out = np.array(retheme(quad_img, PALETTE, k=4))
    assert out[0, 0, :3].tolist() == [255, 0, 0]  # black, the largest region
    assert out[39, 39, :3].tolist() == [255, 255, 0]  # white, the smallest
    assert retheme(quad_img, "#ff0000, #00ff00", k=4).getpixel((0, 0))[:3] == (255, 0, 0)


def test_retheme_unknown_theme(quad_img):
    with pytest.raises(ValueError, match="Unknown theme"):
        retheme(quad_img, "NotATheme")


def test_transparency_survives(sprite):
    out = np.array(retheme(sprite, PALETTE, k=2))
    alpha = np.array(sprite)[..., 3]
    assert (out[..., 3] == alpha).all()
    assert out[8, 8, 3] == 128
    assert {tuple(c) for c in out[alpha > 0][:, :3]} <= set(PALETTE[:2])


def test_luminance_match(quad_img):
    palette = [(250, 250, 200), (10, 10, 60), (90, 90, 140), (170, 170, 220)]
    out = np.array(retheme(quad_img, palette, k=4, match="luminance"))
    assert out[0, 0, :3].tolist() == [10, 10, 60]  # darkest region, darkest color
    assert out[39, 39, :3].tolist() == [250, 250, 200]


def test_overrides_lock_and_pin(quad_img):
    out = np.array(retheme(quad_img, PALETTE, k=4, overrides={0: None, -1: "#123456"}))
    assert out[0, 0, :3].tolist() == [0, 0, 0]  # locked: original pixels
    assert out[39, 39, :3].tolist() == [0x12, 0x34, 0x56]
    with pytest.raises(IndexError):
        retheme(quad_img, PALETTE, k=4, overrides={9: None})


def test_regions_can_be_reused(quad_img):
    regions = find_regions(quad_img, 4)
    a = retheme(quad_img, "Neon", regions=regions)
    b = retheme(quad_img, "Neon", regions=regions.to_dict())  # pre-0.4 format still works
    assert np.array_equal(np.array(a), np.array(b))
    with pytest.raises(TypeError):
        retheme(quad_img, "Neon", regions=[1, 2])


def test_gradient_runs_along_the_image(quad_img):
    out = np.array(retheme(quad_img, PALETTE, k=4, gradient="top-down"))
    column = out[:20, 25, :3].astype(int)  # dark gray region blends toward the next color
    assert not (column[0] == column[-1]).all()
    radial = np.array(retheme(quad_img, PALETTE, k=4, gradient="radial", polarity=0.2))
    assert radial.shape == (40, 40, 4)


def test_gradient_pairs_and_per_region_styles(quad_img):
    regions = find_regions(quad_img, 4)
    targets = [((255, 0, 0), (0, 0, 255)), None, (0, 255, 0), None]
    out = np.array(
        paint(np.array(quad_img), None, regions, targets, gradient=["left-right", None, None, None])
    )
    row = out[5, :20, :3].astype(int)
    assert row[0].tolist() == [255, 0, 0]
    assert row[-1][2] > row[0][2]  # moving toward blue
    assert out[25, 5, :3].tolist() == [170, 170, 170]  # None keeps the original


def test_single_region_gradient_uses_own_shades():
    flat = Image.new("RGB", (10, 10), (100, 100, 100))
    out = np.array(retheme(flat, [(100, 100, 100)], k=1, gradient="top-down"))
    assert out[0, 0, 0] > out[9, 0, 0]


def test_smooth_blends_antialiased_edges():
    arr = np.zeros((10, 30, 3), dtype=np.uint8)
    arr[:, 15:] = 255
    arr[:, 15] = 128  # an anti-aliased edge column
    hard = np.array(retheme(Image.fromarray(arr), [(255, 0, 0), (0, 0, 255)], k=2))
    soft = np.array(retheme(Image.fromarray(arr), [(255, 0, 0), (0, 0, 255)], k=2, smooth=True))
    assert len({tuple(c) for c in hard[:, 15, :3]}) == 1
    assert hard[0, 15, :3].tolist() in ([255, 0, 0], [0, 0, 255])
    edge = soft[0, 15, :3].astype(int)
    assert 0 < edge[0] < 255 and 0 < edge[2] < 255  # in between red and blue
    assert soft[0, 0, :3].tolist() == [255, 0, 0] or soft[0, 0, :3].tolist() == [0, 0, 255]


def test_shading_keeps_texture():
    rng = np.random.default_rng(0)
    base = np.full((20, 20, 3), 120, dtype=np.int16)
    base += rng.integers(-30, 30, (20, 20, 1), dtype=np.int16)
    img = Image.fromarray(base.astype(np.uint8))
    flat = np.array(retheme(img, [(40, 120, 200)], k=1))
    shaded = np.array(retheme(img, [(40, 120, 200)], k=1, shading=True))
    assert len(colors_in(flat)) == 1
    assert len(colors_in(shaded)) > 10
    # Lighter input pixels stay lighter after the recolor
    src = np.array(img)[..., 0].ravel()
    hi, lo = src.argmax(), src.argmin()
    px = shaded[..., :3].reshape(-1, 3)
    assert lightness(px[hi]) > lightness(px[lo])


def test_flood_and_smooth_conflict(quad_img):
    with pytest.raises(ValueError, match="flood and smooth"):
        retheme(quad_img, "Neon", flood=True, smooth=True)
    assert retheme(quad_img, "Neon", flood=True).size == quad_img.size


def test_transfer_palette_luminance(quad_img):
    ref = Image.new("RGB", (10, 10), (200, 30, 30))
    ref.paste((20, 20, 90), (0, 0, 5, 10))
    out = np.array(transfer_palette(quad_img, ref, k=2))
    assert out[0, 0, :3].tolist() == [20, 20, 90]  # black takes the reference's darkest color


def test_retheme_file(tmp_path, quad_path):
    out = retheme_file(quad_path, "Urban", tmp_path / "out", k=2)
    assert out == tmp_path / "out" / "quad_Urban.png"
    assert Image.open(out).size == (40, 40)
    assert retheme_file(quad_path, [(1, 2, 3)], tmp_path, label="mine").name == "quad_mine.png"


def test_gradient_enforce(quad_img, sprite):
    out = gradient_enforce(quad_img, style="top-down", number=4)
    assert out.mode == "RGB"
    column = np.array(out)[:20, 25, 0]
    assert column[0] > column[-1]
    pinned = np.array(gradient_enforce(quad_img, "left-right", color1="#ff0000", color2="blue"))
    assert pinned[0, 0].tolist() == [255, 0, 0]
    assert gradient_enforce(sprite).mode == "RGBA"
    with pytest.warns(DeprecationWarning):
        gradient_enforce(quad_img, "auto", "aggressive")
