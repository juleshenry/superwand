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
from .gradients import gradient_enforce
from PIL import Image
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Enforce gradients on an image.")
    parser.add_argument("image_path", help="Path to the input image.")
    parser.add_argument(
        "--style",
        default="auto",
        choices=[
            "auto",
            "vertical",
            "horizontal",
            "radial",
            "bottom-up",
            "top-down",
            "left-right",
            "right-left",
        ],
        help="Direction of gradients.",
    )
    parser.add_argument(
        "--completeness",
        default="auto",
        choices=["auto", "aggressive", "filter"],
        help="Impacted regions.",
    )
    parser.add_argument("--opacity", default="auto", help="Opacity handling.")
    parser.add_argument(
        "--polarity",
        type=float,
        default=0.5,
        help="Gradient midpoint bias (0.0 to 1.0, default 0.5).",
    )
    parser.add_argument(
        "--color1",
        help="Start color for the gradient (e.g., '255,0,0' or '#FF0000').",
    )
    parser.add_argument(
        "--color2",
        help="End color for the gradient (e.g., '0,0,255' or '#0000FF').",
    )
    parser.add_argument(
        "--output",
        help="Path to the output image. Defaults to 'gradient_<style>_<filename>'.",
    )

    args = parser.parse_args()

    def parse_color(color_str):
        if not color_str:
            return None
        if color_str.startswith("#"):
            color_str = color_str.lstrip("#")
            return tuple(int(color_str[i : i + 2], 16) for i in (0, 2, 4))
        try:
            return tuple(map(int, color_str.split(",")))
        except ValueError:
            raise ValueError(f"Invalid color format: {color_str}")

    try:
        c1 = parse_color(args.color1)
        c2 = parse_color(args.color2)

        img = gradient_enforce(
            args.image_path,
            style=args.style,
            completeness=args.completeness,
            opacity=args.opacity,
            color1=c1,
            color2=c2,
            polarity=args.polarity,
        )

        if args.output:
            output_path = args.output
        else:
            filename = os.path.basename(args.image_path)
            name, ext = os.path.splitext(filename)
            output_path = f"gradient_{args.style}_{name}.png"

        img.save(output_path)
        print(f"Saved gradient enforced image to {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
