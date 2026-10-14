"""
Regenerates every image the README shows.

    uv run python scripts/generate_demos.py            # everything
    uv run python scripts/generate_demos.py demos svg  # just some sections

Sections: themes, charizards, demos, svg, gallery.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from superwand import (
    color_themes,
    contact_sheet,
    extract_palette,
    find_regions,
    gradient_enforce,
    k_sweep,
    retheme,
    svg_retheme,
    theme_cycle_gif,
    transfer_palette,
)
from superwand.gif import label_frame

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
HEIGHT = 360

# Gallery sources and the themes the README shows for each
SIXTEEN = [
    "Spring", "Summer", "Winter", "Fall", "Safari", "Urban", "Neon", "Tropical",
    "Arctic", "Paixão", "Cyberpunk", "Sunset", "Oceanic", "Vaporwave", "Retro80s", "Volcano",
]  # fmt: skip
GALLERY = {
    "erro_xota.jpg": ["Arctic", "Fall", "Neon", "Tropical"],
    "plankt_oct19.jpg": ["Spring", "Summer", "Winter", "Safari"],
    "rio07.jpg": ["Paixão", "Urban", "Arctic", "Fall"],
    "night_portrait.jpg": SIXTEEN,
    "dad_sunglasses.jpg": SIXTEEN,
}
GALLERY_MAX_SIDE = 1400


def load(rel: str, max_side: int = 1200, pixel_art: bool = False) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(ROOT / rel))
    resample = Image.Resampling.NEAREST if pixel_art else Image.Resampling.LANCZOS
    img.thumbnail((max_side, max_side), resample)
    return img


def wrote(path: Path) -> None:
    print("wrote", path.relative_to(ROOT))


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    """Light gray checks, the usual way to show transparency."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    checks = ((yy // cell + xx // cell) % 2).astype(bool)
    arr = np.where(checks[..., None], 205, 245).astype(np.uint8).repeat(3, axis=2)
    return Image.fromarray(arr).convert("RGBA")


def swatch(colors, size: int = HEIGHT) -> Image.Image:
    """A square of horizontal stripes, one per color."""
    img = Image.new("RGB", (size, size))
    band = size / len(colors)
    for i, c in enumerate(colors):
        img.paste(tuple(c), (0, int(i * band), size, int((i + 1) * band)))
    return img


def sheet(tiles, name: str, gap: int = 8) -> None:
    """Lays out (image, label) tiles in a row at a common height."""
    scaled = []
    for img, label in tiles:
        w = round(img.width * HEIGHT / img.height)
        img = img.convert("RGBA").resize((w, HEIGHT), Image.Resampling.LANCZOS)
        if img.getextrema()[3][0] < 255:  # has transparency
            img = Image.alpha_composite(checkerboard(img.size), img)
        scaled.append(label_frame(img, label))
    width = sum(t.width for t in scaled) + gap * (len(scaled) + 1)
    out = Image.new("RGB", (width, HEIGHT + 2 * gap), (255, 255, 255))
    x = gap
    for t in scaled:
        out.paste(t.convert("RGB"), (x, gap))
        x += t.width + gap
    path = EXAMPLES / "demos" / name
    out.save(path, quality=90, method=6)
    wrote(path)


def themes() -> None:
    """2x4 swatches of every built-in theme."""
    out_dir = EXAMPLES / "themes"
    out_dir.mkdir(exist_ok=True)
    for name, colors in color_themes.items():
        img = Image.new("RGB", (200, 100))
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(colors[:8]):
            x, y = (i % 4) * 50, (i // 4) * 50
            draw.rectangle([x, y, x + 50, y + 50], fill=color)
        path = out_dir / f"{name}Theme.jpg"
        img.save(path, quality=95)
        wrote(path)


def charizards() -> None:
    """Every theme and gradient on the Charizard sprite (transparent background kept)."""
    out_dir = EXAMPLES / "charizards"
    sprite = load("examples/images/charizard.png", 560, pixel_art=True)
    regions = find_regions(sprite, 4)
    for name in color_themes:
        path = out_dir / f"{name}_charizard.png"
        retheme(sprite, name, regions=regions).save(path, optimize=True)
        wrote(path)
    for style in ("bottom-up", "top-down", "left-right", "right-left", "radial"):
        path = out_dir / f"gradient_{style}_charizard.png"
        gradient_enforce(sprite, style=style, color1="#ff0000", color2="#0000ff").save(
            path, optimize=True
        )
        wrote(path)


def demos() -> None:
    (EXAMPLES / "demos").mkdir(exist_ok=True)
    charizard = load("examples/images/charizard.png", 360, pixel_art=True)
    rocket = load("examples/images/rocket_vector.jpeg")
    shrimp = load("examples/images/mantis_shrimp.jpeg")
    plankton = load("examples/gallery/plankt_oct19.jpg")
    skyline = load("examples/gallery/erro_xota.jpg")
    portrait = load("examples/gallery/night_portrait.jpg")

    path = EXAMPLES / "demos" / "charizard_themes.gif"
    theme_cycle_gif(charizard, path, k=4, max_size=360, delay=650)
    wrote(path)

    sheet(
        [(rocket, "original")]
        + [(retheme(rocket, "Vaporwave", k=k), f"k = {k}") for k in (2, 4, 6, 8)],
        "k_sweep.webp",
    )
    tiles = k_sweep(rocket, "2,3,4,6,8", ["Vaporwave", "Neon", "Forest", "Volcano"], preview=320)
    path = EXAMPLES / "demos" / "sweep_sheet.webp"
    contact_sheet(tiles, cell=160, title="superwand rocket.jpeg -k 2,3,4,6,8 --sheet").save(
        path, quality=90, method=6
    )
    wrote(path)
    sheet(
        [
            (retheme(rocket, "Vaporwave", gradient="left-right", polarity=p), f"polarity {p}")
            for p in (0.15, 0.5, 0.85)
        ],
        "polarity_sweep.webp",
    )
    sheet(
        [
            (rocket, "original"),
            (swatch(extract_palette(shrimp, 6)), "shrimp palette"),
            (transfer_palette(rocket, shrimp, k=6), "rocket x shrimp"),
            (swatch(extract_palette(plankton, 6)), "plankton palette"),
            (transfer_palette(rocket, plankton, k=6), "rocket x plankton"),
        ],
        "palette_transfer.webp",
    )
    regions = find_regions(skyline, 5)
    sheet(
        [
            (skyline, "original"),
            (retheme(skyline, "Midnight", regions=regions), "match=order"),
            (retheme(skyline, "Midnight", regions=regions, match="luminance"), "match=luminance"),
        ],
        "match_modes.webp",
    )
    regions = find_regions(portrait, 5)
    sheet(
        [
            (portrait, "original"),
            (retheme(portrait, "Tropical", regions=regions), "default"),
            (retheme(portrait, "Tropical", regions=regions, smooth=True), "--smooth"),
            (retheme(portrait, "Tropical", regions=regions, shading=True), "--preserve-shading"),
            (
                retheme(portrait, "Tropical", regions=regions, smooth=True, shading=True),
                "both",
            ),
        ],
        "shading.webp",
    )
    sprite = load("examples/images/charizard.png", 280, pixel_art=True)
    sheet(
        [
            (sprite, "original"),
            (retheme(sprite, "Cyberpunk"), "Cyberpunk"),
            (retheme(sprite, "Arctic", smooth=True), "Arctic, --smooth"),
            (retheme(sprite, "Neon", overrides={2: None}), "Neon, --lock 3"),
        ],
        "transparency.webp",
    )


def svg() -> None:
    src = EXAMPLES / "svg" / "sunset.svg"
    for name in ("Vaporwave", "Forest", "Arctic", "Volcano"):
        path = src.with_name(f"sunset_{name}.svg")
        path.write_text(svg_retheme(src, name, match="luminance"), encoding="utf-8")
        wrote(path)


def gallery() -> None:
    out_dir = EXAMPLES / "gallery"
    for source, names in GALLERY.items():
        img = load(f"examples/gallery/{source}", GALLERY_MAX_SIDE)
        regions = find_regions(img, 4)
        stem = Path(source).stem
        for name in names:
            path = out_dir / f"{stem}_{name}.webp"
            retheme(img, name, regions=regions).convert("RGB").save(path, quality=85, method=6)
            wrote(path)


SECTIONS = {
    "themes": themes,
    "charizards": charizards,
    "demos": demos,
    "svg": svg,
    "gallery": gallery,
}


def main(argv: list[str]) -> None:
    chosen = argv or list(SECTIONS)
    unknown = set(chosen) - set(SECTIONS)
    if unknown:
        sys.exit(f"unknown section(s): {', '.join(sorted(unknown))}; choose from {list(SECTIONS)}")
    for name in chosen:
        SECTIONS[name]()


if __name__ == "__main__":
    main(sys.argv[1:])
