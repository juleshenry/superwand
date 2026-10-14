import math

import numpy as np
import pytest

from superwand.gradients import (
    adjust_color,
    blend_colors,
    calc_gradient_poles,
    clamp,
    gradient_factors,
    normalize_style,
    polarity_exponent,
    twod_dist,
)

SQUARE = [(0, 0), (10, 0), (0, 10), (10, 10)]


def test_clamp_and_distance():
    assert clamp(-1, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert twod_dist((0, 0), (3, 4)) == 5.0


def test_adjust_color():
    assert adjust_color((100, 100, 100), 0.5) == (50, 50, 50)
    assert adjust_color((200, 200, 200), 2.0) == (255, 255, 255)


@pytest.mark.parametrize(
    ("style", "start", "end"),
    [
        ("bottom-up", (5.0, 10), (5.0, 0)),
        ("top-down", (5.0, 0), (5.0, 10)),
        ("left-right", (0, 5.0), (10, 5.0)),
        ("right-left", (10, 5.0), (0, 5.0)),
    ],
)
def test_poles_from_bounding_box(style, start, end):
    assert calc_gradient_poles(style, SQUARE) == (start, end)


def test_radial_poles():
    center, farthest = calc_gradient_poles("radial", SQUARE)
    assert center == (5.0, 5.0)
    assert twod_dist(center, farthest) == pytest.approx(math.sqrt(50))


def test_poles_from_image_size():
    assert calc_gradient_poles("left-right", None, img_size=(11, 5)) == ((0, 2.5), (10, 2.5))
    assert calc_gradient_poles("radial", None, img_size=(10, 10)) == ((5, 5), (9, 9))
    with pytest.raises(ValueError):
        calc_gradient_poles("diagonal", None, img_size=(10, 10))
    with pytest.raises(ValueError):
        calc_gradient_poles("diagonal", SQUARE)


def test_normalize_style():
    assert normalize_style("auto") == "top-down"
    assert normalize_style("horizontal") == "left-right"
    assert normalize_style("none") is None
    assert normalize_style(None) is None
    with pytest.raises(ValueError):
        normalize_style("spiral")


def test_polarity_places_the_midpoint():
    for polarity in (0.2, 0.5, 0.8):
        p = polarity_exponent(polarity)
        assert polarity**p == pytest.approx(0.5)
    factors = gradient_factors([0], [2], "left-right", (0, 0), (10, 0), polarity=0.2)
    assert factors[0] == pytest.approx(0.5)


def test_gradient_factors():
    rows, cols = np.array([0, 5, 10]), np.array([0, 5, 10])
    assert gradient_factors(rows, cols, "top-down", (0, 0), (0, 10)).tolist() == [0, 0.5, 1]
    assert gradient_factors(rows, cols, "right-left", (10, 0), (0, 0)).tolist() == [1, 0.5, 0]
    radial = gradient_factors(rows, cols, "radial", (0, 0), (10, 10))
    assert radial[0] == 0 and radial[-1] == 1
    assert gradient_factors(rows, cols, "top-down", (0, 3), (0, 3)) is None
    with pytest.raises(ValueError):
        gradient_factors(rows, cols, "zigzag", (0, 0), (1, 1))


def test_blend_colors_spaces():
    f = np.array([0.0, 0.5, 1.0])
    srgb = blend_colors((0, 0, 255), (255, 255, 0), f, space="srgb")
    assert srgb[1].tolist() == [127.5, 127.5, 127.5]  # gray midpoint
    oklab = blend_colors((0, 0, 255), (255, 255, 0), f)
    assert oklab[0] == pytest.approx([0, 0, 255], abs=0.01)
    assert oklab[2] == pytest.approx([255, 255, 0], abs=0.01)
    assert oklab[1].max() - oklab[1].min() > 1  # OKLab midpoint is not a pure gray
