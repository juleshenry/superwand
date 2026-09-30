r"""
                                ▂▃▃▃▄▄▄▄▃▂▃▃▂▁
                                ███████▇▃ ▅██▆
                                ▅██████▇▅▁███▃
                                ▄██████▇▃▁██▆▁
                                ▁▇██████▅▃██▅
                             ▁▃  ▇█████▆ ▁██▅ ▁▃▁
                             ███▆▇█████▆▁▁▇█▇▅██▇
                             ▇█████▇▇▇█▇▄▄▇▇▆███▅
                             ▁▃▇██████████████▆▂
                               ▁▁▅██▇▆▇▁▆▇▅█▆▁
                                 ▁▆█▂ ▇▁▁ ▁▆▁
                                  ▃█▇▆▆▇▅▅▇█▃
                               ▁▂▅▇▆▇▇▅▆▅▇▃▆▃▅▃▁
                           ▁▂▄▆▅▃▁▃▆▂▂▄▄▂▁▁▆ ▁▃▆█▆▅▃▁
                          ▂███▆▂  ▁▂▄▃▃▂▂▃▁▅  ▁▄█████▄
                         ▁▇███▅▃▁          ▅  ▂▄▇█████▄▁
                         ▄████▅▁  ▃▁       ▅   ▂███████▂
                         ██████▄  ▄▁       ▅  ▂████████▇▁
                        ▅███████▁ ▃▁  ▂    ▆ ▁▆█████████▄
                       ▂████████▆▁▄▁  ▁   ▁▆▁▆███████████▁
                       ▇█████████▅▄▂▁▁▂▁▂▂▄▆▂████████████▆
                      ▄██████████▆▆█▅▆▆▄▃▃▅▇█████▇▅███████▃
                     ▁██████████████▇▇▅▂ ▁▄██████▇▂████████▁
                    ▁▄▅▄▅▇██▇██████▇▄▆▅▂  ▃███████▃▅█████▇▇▅▁
                    ▂▃    ▂█▆▇████████▆▃ ▁▅███████▄▁██▅▂▁  ▁▄▁
                    ▅▂▂▁▁▁▁▅▁▇██████████▇▆█████████▁▃▆    ▁▂▂▅
                    ▃▃▁▁▆▄▆▅▄██████████████████████▁ ▅▃▂▃▃▃▆▅▂
                   ▂▅▂▄▇▇▆▃ ▂██████████████████████▁ ▁▃▃▆▃▁▂▅▁
                   █▅ ▆▇▆   ▂██████████████████████▁    ▄▁▄▁▁▄
                 ▁▃██▂▅▅▃   ▂██████████████████████▁   ▁▅▄▂▇▁▅
               ▂▅▇▅▃▄▃▂     ▂██████████████████████▁   ▁▃▄▅▇▃▄
            ▁▃▆▆▃▁          ▁██████████████████████▁     ▁▅▅▂
          ▂▄▇▅▁             ▁██████████████████████▁
        ▁▂▆▃▁               ▁██████████▇███████████▁
     ▁▁▁▁▁                  ▁▅█████████▂▄██████████▁
   ▁▁▂▁▁                     ▃█████████▁▃▇█████████▁
▂▁▂▂▁                        ▃█████████▁ ▄█████████
▁▂▁                          ▁▅███████▆  ▃████████▃
                              ▃██████▇▁   ▇███████▂
                               ██████▇    ▁██████▇▂
                               ▂█████▃     ▇█████▁
                               ▂█████▂     ▄█████▁
                              ▂██████▄     ▄█████▆▁
                            ▁▄██████▆▃     ▃██████▇▂
                           ▁█████▆▂▁        ▁▂▅█████▅▁
                            ▂▂▂▂▁              ▁▄▅▇▇▇▂


                                                                     ||`
                                                                     ||
('''' '||  ||` '||''|, .|''|, '||''| '\\    //`  '''|.  `||''|,  .|''||
 `'')  ||  ||   ||  || ||..||  ||      \\/\//   .|''||   ||  ||  ||  ||
`...'  `|..'|.  ||..|' `|...  .||.      \/\/    `|..||. .||  ||. `|..||.
                ||
               .||
                           by Julian Henry
"""

import argparse
import os
from PIL import Image, ImageOps
from .themes import color_themes
from .np_region_identifier import (
    MATCH_MODES,
    extract_palette,
    match_palette,
    np_get_prominent_regions,
    np_inject_theme,
    np_inject_theme_image,
    resolve_theme,
)

GRADIENT_STYLES = [
    "none",
    "auto",
    "vertical",
    "horizontal",
    "radial",
    "bottom-up",
    "top-down",
    "left-right",
    "right-left",
]


def _open(image):
    img = image if isinstance(image, Image.Image) else Image.open(image)
    return ImageOps.exif_transpose(img).convert("RGB")


def retheme(
    image,
    theme,
    k=4,
    flood=False,
    gradient=None,
    polarity=0.5,
    match="order",
    regions=None,
):
    """
    Rethemes an image and returns the result as an RGBA PIL Image.

    image:    path or PIL Image
    theme:    built-in theme name (see `color_themes`) or a list of RGB tuples
    k:        number of color regions to find
    gradient: None or a gradient style (radial, top-down, left-right, ...)
    polarity: where the 50/50 blend of a gradient lands (0.0 to 1.0)
    match:    "order" maps regions to theme colors by prominence,
              "luminance" maps darkest region to darkest color, and so on
    regions:  precomputed np_get_prominent_regions output, to reuse across calls
    """
    img = _open(image)
    if regions is None:
        regions = np_get_prominent_regions(img, number=k)
    theme_rgbs = match_palette(list(regions.keys()), resolve_theme(theme), match)
    style = gradient if gradient and gradient != "none" else None
    return np_inject_theme_image(
        regions,
        theme_rgbs,
        img,
        flood=flood,
        gradient_styles=style,
        gradient_polarities=polarity,
    )


def transfer_palette(image, reference, k=4, match="luminance", **kwargs):
    """Rethemes `image` with the k dominant colors of `reference`."""
    return retheme(image, extract_palette(reference, k), k=k, match=match, **kwargs)


class SuperWand:
    def __init__(self, color_themes, number=4, tolerance=50):
        self.color_themes = color_themes
        self.number = number
        self.tolerance = tolerance

    def apply_theme_to_image(
        self,
        img_path,
        theme_name,
        flood=False,
        gradient_style=None,
        gradient_polarity=0.5,
        output_dir=".",
        match="order",
    ):
        """Saves one output per theme (all themes if theme_name is falsy); returns the paths."""
        regs = np_get_prominent_regions(
            img_path, number=self.number, tolerance=self.tolerance
        )
        themes_to_apply = self.color_themes if not theme_name else [theme_name]
        return [
            np_inject_theme(
                regs,
                t,
                img_path,
                number=self.number,
                flood=flood,
                gradient_styles=gradient_style,
                gradient_polarities=gradient_polarity,
                output_dir=output_dir,
                match=match,
            )
            for t in themes_to_apply
        ]

    def apply_all_themes_to_image(self, img_path, output_dir="."):
        regs = np_get_prominent_regions(
            img_path, number=self.number, tolerance=self.tolerance
        )
        return [
            np_inject_theme(
                regs, theme_name, img_path, number=self.number, output_dir=output_dir
            )
            for theme_name in self.color_themes
        ]


def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb[:3])


def main():
    parser = argparse.ArgumentParser(
        description="Retheme an image with a color palette. "
        "Run with no arguments to launch SuperWand Studio."
    )
    parser.add_argument(
        "image_path", type=str, nargs="?", help="Path to the input image file."
    )
    parser.add_argument(
        "-theme",
        type=str,
        choices=[ct for ct in color_themes],
        help="Theme to apply (Tropical, Urban, Winter, etc.).",
    )
    parser.add_argument(
        "-k", type=int, default=4, help="Number of regions to identify (default 4)."
    )
    parser.add_argument(
        "-tolerance",
        type=int,
        default=50,
        help="Color matching tolerance (default 50).",
    )
    parser.add_argument(
        "-flood", action="store_true", help="Apply morphological flood filling."
    )
    parser.add_argument(
        "-gradient",
        type=str,
        choices=GRADIENT_STYLES,
        default="none",
        help="Gradient style to apply.",
    )
    parser.add_argument(
        "-polarity",
        type=float,
        default=0.5,
        help="Where along the gradient the 50/50 blend lands (0.0 to 1.0, default 0.5).",
    )
    parser.add_argument(
        "-match",
        choices=MATCH_MODES,
        default=None,
        help="How regions are paired with palette colors: 'order' (by prominence, "
        "default for themes) or 'luminance' (dark to dark, default for -palette-from).",
    )
    parser.add_argument(
        "-palette-from",
        dest="palette_from",
        metavar="REFERENCE_IMAGE",
        help="Steal the k dominant colors of another image and use them as the theme.",
    )
    parser.add_argument(
        "-gif",
        action="store_true",
        help="Write an animated GIF cycling through every theme (or just -theme).",
    )
    parser.add_argument(
        "-palette",
        action="store_true",
        help="Print the image's k dominant colors as hex and exit.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=".",
        help="Directory for output files (default: current directory).",
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="List available themes and exit."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode without opening the studio.",
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Studio port (default 5001)."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Run the studio in Flask debug mode."
    )

    args = parser.parse_args()

    if args.list_themes:
        for name, colors in color_themes.items():
            print(f"{name:<10} " + " ".join(_hex(c) for c in colors))
        return

    wants_output = args.theme or args.palette_from or args.gif or args.palette
    if not args.headless and not wants_output:
        from ..studio.app import app

        app.run(debug=args.debug, port=args.port)
        return

    if not args.image_path:
        print(
            "Error: image_path is required when running in headless mode or applying a theme."
        )
        return

    gradient = args.gradient if args.gradient != "none" else None
    stem = os.path.splitext(os.path.basename(args.image_path))[0]

    if args.palette:
        for rgb in extract_palette(args.image_path, args.k):
            print(_hex(rgb), rgb)
        return

    if args.gif:
        from ..utils.gif_maker import theme_cycle_gif

        themes = [args.theme] if args.theme else list(color_themes)
        os.makedirs(args.output_dir, exist_ok=True)
        out = os.path.join(args.output_dir, f"{stem}_themes.gif")
        theme_cycle_gif(
            args.image_path,
            out,
            themes=themes,
            k=args.k,
            gradient=gradient,
            polarity=args.polarity,
            match=args.match or "order",
        )
        print(f"Saved {out}")
        return

    if args.palette_from:
        img = transfer_palette(
            args.image_path,
            args.palette_from,
            k=args.k,
            match=args.match or "luminance",
            flood=args.flood,
            gradient=gradient,
            polarity=args.polarity,
        )
        ref = os.path.splitext(os.path.basename(args.palette_from))[0]
        os.makedirs(args.output_dir, exist_ok=True)
        out = os.path.join(args.output_dir, f"{stem}_from_{ref}.png")
        img.save(out)
        print(f"Saved {out}")
        return

    sw = SuperWand(color_themes, number=args.k, tolerance=args.tolerance)
    saved = sw.apply_theme_to_image(
        args.image_path,
        args.theme,
        flood=args.flood,
        gradient_style=gradient,
        gradient_polarity=args.polarity,
        output_dir=args.output_dir,
        match=args.match or "order",
    )
    for path in saved or []:
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
