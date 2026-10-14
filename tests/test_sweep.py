import numpy as np
import pytest
from PIL import Image

from superwand import contact_sheet, find_regions, k_sweep, parse_k_values, retheme
from superwand.sweep import SweepTile, checkerboard, downsample


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        (4, [4]),
        ("4", [4]),
        ("2,3,4,6,8", [2, 3, 4, 6, 8]),
        ("2-5", [2, 3, 4, 5]),
        ("8, 2-4, 3", [2, 3, 4, 8]),
        ([6, 2, 2], [2, 6]),
    ],
)
def test_parse_k_values(spec, expected):
    assert parse_k_values(spec) == expected


@pytest.mark.parametrize("bad", ["", "x", "2-", "5-2", "0", "65", "2-9-1", [0]])
def test_parse_k_values_rejects(bad):
    with pytest.raises(ValueError):
        parse_k_values(bad)


def test_k_sweep_finds_regions_once_per_k(quad_img):
    calls = []

    def regions_for(k):
        calls.append(k)
        return find_regions(quad_img, k)

    tiles = k_sweep(quad_img, "2-4", ["Neon", "Arctic", "#ff0000,#00ff00"], regions_for=regions_for)
    assert calls == [2, 3, 4]
    assert [(t.theme, t.k) for t in tiles] == [
        (theme, k) for theme in ("Neon", "Arctic", "custom") for k in (2, 3, 4)
    ]
    # Each tile is exactly what retheme() makes for that combination
    expected = retheme(quad_img, "Arctic", k=3)
    arctic3 = next(t for t in tiles if t.theme == "Arctic" and t.k == 3)
    assert np.array_equal(np.array(arctic3.image), np.array(expected))


def test_k_sweep_defaults_to_every_theme(quad_img):
    from superwand import color_themes

    tiles = k_sweep(quad_img, 2)
    assert {t.theme for t in tiles} == set(color_themes)


def test_sweeps_are_reproducible_beyond_the_palette_length():
    noise = np.random.default_rng(3).integers(0, 256, (60, 60, 3), dtype=np.uint8)
    img = Image.fromarray(noise)
    a = k_sweep(img, "10,12", ["Neon"], seed=7)
    b = k_sweep(img, "10,12", ["Neon"], seed=7)
    for x, y in zip(a, b, strict=True):
        assert np.array_equal(np.array(x.image), np.array(y.image))
    # 12 regions with an 8-color theme: colors cycle instead of being picked at random
    used = {tuple(c) for c in np.array(a[1].image)[..., :3].reshape(-1, 3)}
    from superwand import color_themes

    assert used <= set(color_themes["Neon"])


def test_preview_tiles_use_the_full_image_regions(sprite):
    tiles = k_sweep(sprite, [2], ["Neon"], preview=16)
    assert tiles[0].image.size == (16, 16)
    full = np.array(retheme(sprite, "Neon", k=2))
    assert np.array_equal(np.array(tiles[0].image), full[::2, ::2])


def test_downsample_is_a_no_op_for_small_images(quad_img):
    regions = find_regions(quad_img, 2)
    rgb = np.array(quad_img)
    out = downsample(rgb, None, regions, 100)
    assert out[2] is regions and out[0] is rgb


def test_contact_sheet_layout(quad_img, sprite):
    tiles = [
        SweepTile(theme, k, retheme(sprite, theme, k=k))
        for theme in ("Neon", "Volcano")
        for k in (2, 3, 4)
    ]
    sheet = contact_sheet(tiles, cell=50, title="sprite.png")
    assert sheet.mode == "RGB"
    assert sheet.width > 3 * 50 and sheet.height > 2 * 50
    with pytest.raises(ValueError):
        contact_sheet([])


def test_checkerboard():
    board = np.array(checkerboard((16, 8), cell=4))
    assert board.shape == (8, 16, 4)
    assert board[0, 0, 0] != board[0, 4, 0]
