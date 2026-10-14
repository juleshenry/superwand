"""Animated GIFs that cycle an image through themes."""

from __future__ import annotations

from collections.abc import Sequence
from os import PathLike

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .regions import ImageInput, load_image, regions_from_array
from .render import retheme
from .themes import Theme, all_themes, theme_label


def label_frame(img: Image.Image, text: str) -> Image.Image:
    """Draws `text` in a dark bar along the bottom of the image."""
    img = img.convert("RGBA")
    size = max(14, img.height // 18)
    font = ImageFont.load_default(size=size)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bar = int(size * 1.6)
    draw.rectangle([0, img.height - bar, img.width, img.height], fill=(0, 0, 0, 150))
    draw.text(
        (size // 2, img.height - bar / 2), text, font=font, fill=(255, 255, 255, 255), anchor="lm"
    )
    out = Image.alpha_composite(img, overlay)
    # Keep the bar readable over transparent areas, which GIF can't render translucent
    arr = np.array(out)
    arr[img.height - bar :, :, 3] = 255
    return Image.fromarray(arr, "RGBA")


def theme_cycle_gif(
    image: ImageInput,
    output_path: str | PathLike[str],
    themes: Sequence[Theme] | None = None,
    k: int = 4,
    delay: int = 700,
    max_size: int = 480,
    label: bool = True,
    **retheme_kwargs: object,
) -> str | PathLike[str]:
    """
    Writes an animated GIF that cycles `image` through `themes` (default: all).
    Regions are computed once and reused for every frame.
    """
    rgb, alpha = load_image(image)
    img = (
        Image.fromarray(rgb) if alpha is None else Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    )
    img.thumbnail((max_size, max_size))
    rgb, alpha = load_image(img)
    regions = regions_from_array(rgb, alpha, k)

    frames = []
    for theme in themes or list(all_themes()):
        frame = retheme(img, theme, k=k, regions=regions, **retheme_kwargs)  # type: ignore[arg-type]
        frames.append(label_frame(frame, theme_label(theme)) if label else frame)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=delay,
        loop=0,
        disposal=2,
    )
    return output_path
