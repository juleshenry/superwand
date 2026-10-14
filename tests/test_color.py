import numpy as np
import pytest

from superwand.color import (
    contrast_ratio,
    ensure_contrast,
    hex_to_rgb,
    hsl_to_rgb,
    lightness,
    oklab_to_rgb,
    oklab_to_srgb,
    parse_color,
    parse_css_color,
    parse_palette,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_oklab,
    split_args,
    srgb_to_oklab,
)


@pytest.mark.parametrize(
    ("text", "rgb"),
    [
        ("#f80", (255, 136, 0)),
        ("ff8800", (255, 136, 0)),
        ("#FF8800", (255, 136, 0)),
        ("hotpink", (255, 105, 180)),
        ("RebeccaPurple", (102, 51, 153)),
        ("255, 0, 128", (255, 0, 128)),
        ("rgb(255 0 128 / 50%)", (255, 0, 128)),
        ("rgba(100%, 0%, 50%, .5)", (255, 0, 128)),
        ("hsl(120, 100%, 25%)", (0, 128, 0)),
        ("hsl(0.5turn 100% 50%)", (0, 255, 255)),
        ("oklch(0.628 0.2577 29.23)", (255, 0, 0)),
        ("oklab(62.8% 0.2249 0.1258)", (255, 0, 0)),
        ((300, -5, 12), (255, 0, 12)),
    ],
)
def test_parse_color(text, rgb):
    assert parse_color(text) == rgb


@pytest.mark.parametrize("bad", ["", "#12", "rgb(1,2)", "notacolor", (1, 2)])
def test_parse_color_rejects(bad):
    with pytest.raises(ValueError):
        parse_color(bad)


def test_parse_css_color_keeps_alpha_as_written():
    assert parse_css_color("#11223380") == ((17, 34, 51), "80")
    assert parse_css_color("#1238") == ((17, 34, 51), "88")
    assert parse_css_color("rgba(10,20,30,.5)") == ((10, 20, 30), ".5")
    assert parse_css_color("hsl(0 0% 0% / 25%)") == ((0, 0, 0), "25%")
    assert parse_css_color("calc(1px)") is None


def test_split_args():
    assert split_args("1, 2, 3, .5") == (["1", "2", "3"], ".5")
    assert split_args("1 2 3 / 50%") == (["1", "2", "3"], "50%")


def test_parse_palette_splits_outside_functions():
    assert parse_palette("#ff0080, rgb(0, 255, 255) navy") == [
        (255, 0, 128),
        (0, 255, 255),
        (0, 0, 128),
    ]
    assert parse_palette([(1, 2, 3), "#000"]) == [(1, 2, 3), (0, 0, 0)]
    with pytest.raises(ValueError):
        parse_palette("")


@pytest.mark.parametrize("rgb", [(0, 0, 0), (255, 255, 255), (255, 0, 0), (12, 200, 77), (1, 2, 3)])
def test_round_trips(rgb):
    assert oklab_to_rgb(rgb_to_oklab(rgb)) == rgb
    assert hsl_to_rgb(rgb_to_hsl(rgb)) == rgb
    assert hex_to_rgb(rgb_to_hex(rgb)) == rgb


def test_oklab_reference_values():
    # White is L=1 with no chroma; sRGB red per Ottosson's reference implementation
    assert rgb_to_oklab((255, 255, 255)) == pytest.approx((1, 0, 0), abs=1e-6)
    assert rgb_to_oklab((255, 0, 0)) == pytest.approx((0.62796, 0.22486, 0.12585), abs=1e-4)


def test_vectorized_oklab_matches_scalar():
    pixels = np.random.default_rng(1).integers(0, 256, (50, 3), dtype=np.uint8)
    fast = srgb_to_oklab(pixels)  # uint8 takes the float32 path
    exact = np.array([rgb_to_oklab(p) for p in pixels.astype(float)])
    assert np.allclose(fast, exact, atol=1e-5)
    assert np.allclose(oklab_to_srgb(exact), pixels, atol=0.01)


def test_lightness_orders_colors():
    assert lightness((0, 0, 0)) < lightness((0, 0, 255)) < lightness((255, 255, 0)) < 1.0001


def test_contrast_ratio_extremes():
    assert contrast_ratio((0, 0, 0), (255, 255, 255)) == pytest.approx(21)
    assert contrast_ratio((10, 20, 30), (10, 20, 30)) == pytest.approx(1)


@pytest.mark.parametrize(
    ("fg", "bg"), [((200, 200, 255), (255, 255, 255)), ((40, 40, 90), (20, 20, 30))]
)
def test_ensure_contrast_reaches_target(fg, bg):
    fixed = ensure_contrast(fg, bg, 4.5)
    assert contrast_ratio(fixed, bg) >= 4.5
    assert fixed != fg


def test_ensure_contrast_leaves_readable_colors_alone():
    assert ensure_contrast((0, 0, 0), (255, 255, 255)) == (0, 0, 0)


def test_ensure_contrast_falls_back_to_black_or_white():
    assert ensure_contrast((128, 128, 128), (119, 119, 119), 21) in {(0, 0, 0), (255, 255, 255)}
