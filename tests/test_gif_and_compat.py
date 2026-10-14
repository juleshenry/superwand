from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import superwand
from superwand.gif import label_frame, theme_cycle_gif


def test_theme_cycle_gif(tmp_path, quad_img):
    path = tmp_path / "cycle.gif"
    theme_cycle_gif(quad_img, path, themes=["Neon", "Arctic", "#ff0000,#0000ff"], k=4)
    with Image.open(path) as gif:
        assert gif.n_frames == 3


def test_gif_keeps_transparency(tmp_path, sprite):
    path = tmp_path / "sprite.gif"
    theme_cycle_gif(sprite, path, themes=["Neon"], k=2, label=False)
    with Image.open(path) as gif:
        assert np.array(gif.convert("RGBA"))[0, 0, 3] == 0


def test_label_frame_draws_an_opaque_bar(sprite):
    out = np.array(label_frame(sprite, "Neon"))
    assert (out[-1, :, 3] == 255).all()


def test_public_api():
    assert superwand.__version__
    for name in superwand.__all__:
        assert hasattr(superwand, name), name
    with pytest.raises(AttributeError):
        _ = superwand.not_a_thing


def test_deprecated_names_still_work(tmp_path, quad_path):
    with pytest.warns(DeprecationWarning, match="find_regions"):
        legacy = superwand.np_get_prominent_regions(str(quad_path), number=4)
    assert len(legacy[(0, 0, 0)]) == 700

    with pytest.warns(DeprecationWarning, match="retheme_file"):
        out = superwand.np_inject_theme(legacy, "Neon", str(quad_path), output_dir=tmp_path)
    assert out.endswith("quad_Neon.png")

    with pytest.warns(DeprecationWarning, match="SuperWand"):
        wand = superwand.SuperWand(superwand.color_themes, 2)
    saved = wand.apply_theme_to_image(str(quad_path), "Urban", output_dir=tmp_path)
    assert [Path(p).name for p in saved] == ["quad_Urban.png"]
    assert len(wand.apply_all_themes_to_image(str(quad_path), output_dir=tmp_path)) == 18
