import warnings

import numpy as np
import pytest
from PIL import Image

from superwand.regions import Regions, extract_palette, find_regions, load_image


def test_regions_are_sorted_and_cover_every_pixel(quad_img):
    regions = find_regions(quad_img, 4)
    assert regions.colors[0] == (0, 0, 0)
    assert regions.counts == [700, 400, 400, 100]
    assert sorted(regions.colors[1:3]) == [(80, 80, 80), (170, 170, 170)]
    assert regions.labels.shape == (40, 40)
    assert (regions.labels >= 0).all()
    assert len(regions) == 4


def test_regions_are_deterministic(quad_img):
    a, b = find_regions(quad_img, 3), find_regions(quad_img, 3)
    assert a.colors == b.colors
    assert (a.labels == b.labels).all()


def test_fewer_colors_than_k_has_no_warnings():
    two = np.zeros((20, 20, 3), dtype=np.uint8)
    two[:, 10:] = 255
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        regions = find_regions(Image.fromarray(two), 6)
    assert regions.colors == [(0, 0, 0), (255, 255, 255)]


def test_transparent_pixels_are_excluded(sprite):
    regions = find_regions(sprite, 4)
    alpha = np.array(sprite)[..., 3]
    assert (regions.labels[alpha == 0] == -1).all()
    assert (regions.labels[alpha > 0] >= 0).all()
    assert len(regions) == 2  # only red and blue exist among visible pixels


def test_fully_transparent_image():
    regions = find_regions(Image.new("RGBA", (5, 5)), 4)
    assert len(regions) == 0
    assert (regions.labels == -1).all()


def test_rgb_space_and_bad_arguments(quad_img):
    assert find_regions(quad_img, 4, space="rgb").colors[0] == (0, 0, 0)
    with pytest.raises(ValueError):
        find_regions(quad_img, 0)
    with pytest.raises(ValueError):
        find_regions(quad_img, 4, space="hsv")


def test_large_images_are_sampled(monkeypatch):
    noise = np.random.default_rng(0).integers(0, 256, (300, 300, 3), dtype=np.uint8)
    regions = find_regions(Image.fromarray(noise), 5, max_samples=1000)
    assert sum(regions.counts) == 300 * 300


def test_legacy_dict_round_trip(quad_img):
    regions = find_regions(quad_img, 4)
    legacy = regions.to_dict()
    assert list(legacy) == regions.colors
    assert len(legacy[(0, 0, 0)]) == 700
    rebuilt = Regions.from_dict(legacy, regions.shape)
    assert (rebuilt.labels == regions.labels).all()
    assert rebuilt.colors == regions.colors


def test_soft_assignment_weights(quad_img):
    regions = find_regions(quad_img, 4)
    arr = np.array(quad_img)
    second, weight = regions.soft_assignment(arr)
    assert second.shape == weight.shape == (40, 40)
    assert np.allclose(weight, 1, atol=1e-3)  # flat regions sit on their centers
    assert (second != regions.labels).all()
    assert regions.soft_assignment(arr)[0] is second  # cached


def test_load_image_modes(tmp_path, sprite):
    rgb, alpha = load_image(sprite)
    assert rgb.shape == (32, 32, 3) and alpha is not None
    rgb, alpha = load_image(Image.new("L", (3, 3), 128))
    assert alpha is None and rgb[0, 0].tolist() == [128, 128, 128]
    p = Image.new("P", (2, 2))
    p.info["transparency"] = 0
    assert load_image(p)[1] is not None


def test_extract_palette(quad_img, tmp_path):
    path = tmp_path / "q.png"
    quad_img.save(path)
    palette = extract_palette(str(path), 4)
    assert len(palette) == 4
    assert palette[0] == (0, 0, 0)
