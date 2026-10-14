"""Pre-0.4 names, kept working for one release with a DeprecationWarning."""

from __future__ import annotations

import warnings
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path

import numpy as np
import numpy.typing as npt

from .color import RGB
from .regions import ImageInput, Regions, find_regions, load_image
from .render import retheme
from .themes import all_themes, theme_label


def _warn(old: str, new: str) -> None:
    warnings.warn(
        f"superwand.{old} is deprecated and will be removed in 0.5; use {new}",
        DeprecationWarning,
        stacklevel=3,
    )


def np_get_prominent_regions(
    ip: ImageInput, number: int = 4, tolerance: int = 50, seed: int = 42
) -> OrderedDict[RGB, npt.NDArray[np.intp]]:
    """Deprecated: use find_regions(), which returns a Regions object."""
    _warn("np_get_prominent_regions()", "find_regions()")
    return find_regions(ip, number, seed=seed).to_dict()


def np_inject_theme(
    cpd: Regions | Mapping[Sequence[int], npt.ArrayLike],
    theme_name: str,
    image_path: str | PathLike[str],
    number: int = 4,
    flood: bool = False,
    gradient_styles: str | None = None,
    gradient_polarities: float | None = None,
    output_dir: str | PathLike[str] = ".",
    match: str = "order",
    palette: Sequence[Sequence[int]] | None = None,
) -> str:
    """Deprecated: use retheme_file() or retheme()."""
    _warn("np_inject_theme()", "retheme_file()")
    rgb, _ = load_image(image_path)
    regions = (
        cpd if isinstance(cpd, Regions) else Regions.from_dict(cpd, (rgb.shape[0], rgb.shape[1]))
    )
    img = retheme(
        image_path,
        palette if palette is not None else theme_name,
        k=number,
        flood=flood,
        gradient=gradient_styles,
        polarity=0.5 if gradient_polarities is None else gradient_polarities,
        match=match,
        regions=regions,
    )
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{Path(image_path).stem}_{theme_name}.png"
    img.save(out)
    return str(out)


class SuperWand:
    """Deprecated: use retheme() / retheme_file()."""

    def __init__(
        self,
        color_themes: Mapping[str, Sequence[Sequence[int]]] | None = None,
        number: int = 4,
        tolerance: int = 50,
    ) -> None:
        _warn("SuperWand", "retheme() or retheme_file()")
        self.color_themes = dict(color_themes) if color_themes is not None else all_themes()
        self.number = number
        self.tolerance = tolerance

    def apply_theme_to_image(
        self,
        img_path: str | PathLike[str],
        theme_name: str | None,
        flood: bool = False,
        gradient_style: str | None = None,
        gradient_polarity: float = 0.5,
        output_dir: str | PathLike[str] = ".",
        match: str = "order",
    ) -> list[str]:
        """Saves one output per theme (all themes if theme_name is falsy); returns the paths."""
        regions = find_regions(img_path, self.number)
        names = [theme_name] if theme_name else list(self.color_themes)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for name in names:
            theme = self.color_themes.get(name, name)
            img = retheme(
                img_path,
                theme,
                k=self.number,
                flood=flood,
                gradient=gradient_style,
                polarity=gradient_polarity,
                match=match,
                regions=regions,
            )
            out = out_dir / f"{Path(img_path).stem}_{theme_label(name)}.png"
            img.save(out)
            saved.append(str(out))
        return saved

    def apply_all_themes_to_image(
        self, img_path: str | PathLike[str], output_dir: str | PathLike[str] = "."
    ) -> list[str]:
        return self.apply_theme_to_image(img_path, None, output_dir=output_dir)
