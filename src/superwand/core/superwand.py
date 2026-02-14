"""
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
from .themes import color_themes
from .np_region_identifier import np_get_prominent_regions, np_inject_theme


class Img:
    pass


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
        gradient_intensity=0.2,
    ):
        regs = np_get_prominent_regions(
            img_path, number=self.number, tolerance=self.tolerance
        )
        themes_to_apply = self.color_themes if not theme_name else [theme_name]
        for t in themes_to_apply:
            np_inject_theme(
                regs,
                t,
                img_path,
                number=self.number,
                flood=flood,
                gradient_styles=gradient_style,
                gradient_intensities=gradient_intensity,
            )

    def apply_all_themes_to_image(self, img_path):
        regs = np_get_prominent_regions(
            img_path, number=self.number, tolerance=self.tolerance
        )
        for theme_name in self.color_themes:
            np_inject_theme(regs, theme_name, img_path, number=self.number)


def main():
    parser = argparse.ArgumentParser(
        description="Process an image with a specified theme."
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
        choices=["none", "auto", "vertical", "horizontal", "radial"],
        default="none",
        help="Gradient style to apply.",
    )
    parser.add_argument(
        "-intensity",
        type=float,
        default=0.2,
        help="Gradient intensity (0.0 to 1.0, default 0.2).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode without opening the studio.",
    )

    args = parser.parse_args()

    if not args.headless and not args.theme:
        from ..studio.app import app

        app.run(debug=True, port=5001)
        return

    sw = SuperWand(color_themes, number=args.k, tolerance=args.tolerance)
    if not args.image_path:
        print(
            "Error: image_path is required when running in headless mode or applying a theme."
        )
        return
    sw.apply_theme_to_image(
        args.image_path,
        args.theme,
        flood=args.flood,
        gradient_style=args.gradient if args.gradient != "none" else None,
        gradient_intensity=args.intensity,
    )


if __name__ == "__main__":
    main()
