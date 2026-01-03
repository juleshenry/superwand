import pytest
from superwand.gradients import clamp, twod_dist, calc_gradient_poles, adjust_color

def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10

def test_twod_dist():
    assert twod_dist((0, 0), (3, 4)) == 5.0
    assert twod_dist((1, 1), (1, 1)) == 0.0
    assert twod_dist((0, 0), (0, 5)) == 5.0

def test_adjust_color():
    assert adjust_color((100, 100, 100), 1.0) == (100, 100, 100)
    assert adjust_color((100, 100, 100), 0.5) == (50, 50, 50)
    assert adjust_color((100, 100, 100), 2.0) == (200, 200, 200)
    assert adjust_color((200, 200, 200), 2.0) == (255, 255, 255) # Clamping
    assert adjust_color((100, 100, 100), 0.0) == (0, 0, 0)

def test_calc_gradient_poles_bottom_up():
    pixel_arr = [(0, 0), (10, 0), (0, 10), (10, 10)]
    start, end = calc_gradient_poles("bottom-up", pixel_arr)
    # mid_x = 5.0, min_y = 0, max_y = 10
    assert start == (5.0, 0)
    assert end == (5.0, 10)

def test_calc_gradient_poles_top_down():
    pixel_arr = [(0, 0), (10, 0), (0, 10), (10, 10)]
    start, end = calc_gradient_poles("top-down", pixel_arr)
    # mid_x = 5.0, min_y = 0, max_y = 10
    assert start == (5.0, 10)
    assert end == (5.0, 0)

def test_calc_gradient_poles_left_right():
    pixel_arr = [(0, 0), (10, 0), (0, 10), (10, 10)]
    start, end = calc_gradient_poles("left-right", pixel_arr)
    # mid_y = 5.0, min_x = 0, max_x = 10
    assert start == (0, 5.0)
    assert end == (10, 5.0)

def test_calc_gradient_poles_right_left():
    pixel_arr = [(0, 0), (10, 0), (0, 10), (10, 10)]
    start, end = calc_gradient_poles("right-left", pixel_arr)
    # mid_y = 5.0, min_x = 0, max_x = 10
    assert start == (10, 5.0)
    assert end == (0, 5.0)

def test_calc_gradient_poles_radial():
    pixel_arr = [(0, 0), (10, 0), (0, 10), (10, 10)]
    # center = (5.0, 5.0)
    # farthest points are (0,0), (10,0), (0,10), (10,10) - all dist sqrt(50) approx 7.07
    center, farthest = calc_gradient_poles("radial", pixel_arr)
    assert center == (5.0, 5.0)
    # Farthest could be any of the corners, check distance
    assert twod_dist(center, farthest) == pytest.approx(7.0710678)

def test_calc_gradient_poles_invalid():
    with pytest.raises(ValueError):
        calc_gradient_poles("invalid", [])
