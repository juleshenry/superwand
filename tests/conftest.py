import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def quad_img():
    """Four flat regions: black (700 px), dark gray (400), light gray (400), white (100)."""
    arr = np.zeros((40, 40, 3), dtype=np.uint8)
    arr[:20, 20:] = (80, 80, 80)
    arr[20:, :20] = (170, 170, 170)
    arr[30:, 30:] = (250, 250, 250)
    return Image.fromarray(arr)


@pytest.fixture
def sprite():
    """A red/blue sprite on a fully transparent background, with a half-transparent pixel."""
    arr = np.zeros((32, 32, 4), dtype=np.uint8)
    arr[8:24, 8:16] = (220, 30, 30, 255)
    arr[8:24, 16:24] = (30, 30, 220, 255)
    arr[8, 8] = (220, 30, 30, 128)
    return Image.fromarray(arr, "RGBA")


@pytest.fixture
def quad_path(tmp_path, quad_img):
    path = tmp_path / "quad.png"
    quad_img.save(path)
    return path


@pytest.fixture(autouse=True)
def isolated_user_themes(tmp_path, monkeypatch):
    """Point the user themes folder at an empty temp dir so local themes don't leak in."""
    folder = tmp_path / "user-themes"
    monkeypatch.setenv("SUPERWAND_THEMES_DIR", str(folder))
    return folder
