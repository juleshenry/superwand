"""Regenerates the demo images in examples/demos/. Run: uv run python scripts/generate_demos.py"""

import os
import sys

from PIL import Image, ImageOps

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from superwand import (  # noqa: E402
    extract_palette,
    np_get_prominent_regions,
    retheme,
    theme_cycle_gif,
    transfer_palette,
)
from superwand.utils.gif_maker import label_frame  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "examples", "demos")
HEIGHT = 360


def load(rel, max_side=1200):
    img = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, rel))).convert("RGB")
    img.thumbnail((max_side, max_side))
    return img


def swatch(colors, size=HEIGHT):
    """A square made of horizontal stripes, one per color."""
    img = Image.new("RGB", (size, size))
    band = size / len(colors)
    for i, c in enumerate(colors):
        img.paste(tuple(c), (0, int(i * band), size, int((i + 1) * band)))
    return img


def sheet(tiles, name, gap=8):
    """Lays out (image, label) tiles in a row at a common height and saves it."""
    scaled = []
    for img, label in tiles:
        w = round(img.width * HEIGHT / img.height)
        scaled.append(label_frame(img.convert("RGB").resize((w, HEIGHT)), label))
    width = sum(t.width for t in scaled) + gap * (len(scaled) + 1)
    out = Image.new("RGB", (width, HEIGHT + 2 * gap), (255, 255, 255))
    x = gap
    for t in scaled:
        out.paste(t, (x, gap), t)
        x += t.width + gap
    path = os.path.join(OUT, name)
    out.save(path, optimize=True)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    os.makedirs(OUT, exist_ok=True)
    charizard = load("examples/images/charizard.png", 800)
    rocket = load("examples/images/rocket_vector.jpeg")
    shrimp = load("examples/images/mantis_shrimp.jpeg")
    plankton = load("examples/gallery/plankt_oct19.jpg")
    skyline = load("examples/gallery/erro_xota.jpg")

    # 1. Every theme, one GIF
    path = os.path.join(OUT, "charizard_themes.gif")
    theme_cycle_gif(charizard, path, k=4, max_size=360, delay=650)
    print("wrote", os.path.relpath(path, ROOT))

    # 2. How -k changes the result on flat vector art
    sheet(
        [(rocket, "original")]
        + [(retheme(rocket, "Vaporwave", k=k), f"k = {k}") for k in (2, 4, 6, 8)],
        "k_sweep.png",
    )

    # 3. Gradient polarity: where the 50/50 blend lands
    sheet(
        [
            (
                retheme(rocket, "Vaporwave", gradient="left-right", polarity=p),
                f"left-right, polarity {p}",
            )
            for p in (0.15, 0.5, 0.85)
        ],
        "polarity_sweep.png",
    )

    # 4. Palette transfer from a reference photo
    sheet(
        [
            (rocket, "original"),
            (swatch(extract_palette(shrimp, 6)), "shrimp palette"),
            (transfer_palette(rocket, shrimp, k=6), "rocket x shrimp"),
            (swatch(extract_palette(plankton, 6)), "plankton palette"),
            (transfer_palette(rocket, plankton, k=6), "rocket x plankton"),
        ],
        "palette_transfer.png",
    )

    # 5. Region matching: by prominence vs by luminance
    regions = np_get_prominent_regions(skyline, number=5)
    sheet(
        [
            (skyline, "original"),
            (retheme(skyline, "Midnight", regions=regions), "Midnight, match=order"),
            (
                retheme(skyline, "Midnight", regions=regions, match="luminance"),
                "Midnight, match=luminance",
            ),
        ],
        "match_modes.png",
    )


if __name__ == "__main__":
    main()
