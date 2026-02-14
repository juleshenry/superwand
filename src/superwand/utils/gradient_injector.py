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

import os
from math import sqrt
from ..core.region_identifier import get_prominent_regions
from PIL import Image, ImageDraw, ImageFont
from .gradients import paste_gradient, calc_gradient_poles
import numpy as np
from .prompt_input import prompt_input
import math


def create_image(rgb_tuples, grid_size, cell_size):
    width = grid_size[0] * cell_size
    height = grid_size[1] * cell_size
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "arial.ttf"
    )
    choice_font = ImageFont.truetype(font=font_path, size=36)
    for i, (r, g, b) in enumerate(rgb_tuples):
        x = (i % grid_size[0]) * cell_size
        y = (i // grid_size[0]) * cell_size
        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(r, g, b))
        label = f"({r}, {g}, {b})"
        draw.text(
            (x + 5, y + 5),
            label,
            font=font,
            fill=("black" if (r + g + b > 100) else "white"),
        )
        draw.text(
            (
                x + cell_size // 3,
                y + cell_size // 3,
            ),
            str(i + 1),
            font=choice_font,
            fill=(
                abs(255 - r),
                abs(255 - g),
                abs(255 - b),
            ),
        )

    return image


def create_image_prompt(ip: str):
    color_numbers = 16
    prs = get_prominent_regions(ip, number=color_numbers)
    grid_size = int(round(sqrt(color_numbers), 0))
    grid_size = (
        grid_size,
        grid_size,
    )
    cell_size = 100
    prompt_image = create_image(prs.keys(), grid_size, cell_size)
    return prompt_image, prs


def prompted_single_change():
    # Choose base image
    ip = "./examples/images/charizard.png"
    # Create image prompt to allow choice, get prominent regions
    prompt_image, prs = create_image_prompt(ip)
    # Show prompt of color grid and replace.
    modified_image = prompt_input(
        Image.open(ip).convert("RGB"), prompt_image, prs, error=3
    )
    modified_image.save("modified_" + ip.split("/")[-1])


def gradient_single_change(start_color, end_color, grad_dir, color_to_replace=None):
    ip = "./examples/images/rocket_vector.jpeg"
    if not color_to_replace:
        pixel_regions = get_prominent_regions(ip, number=10)
        color, polygon = list(pixel_regions.items())[1]
    print("Replacing color:", color)
    polygon = [tuple(p) for p in polygon]
    img = Image.open(ip).convert("RGB")
    injected = inject_gradient(img, polygon, start_color, end_color, grad_dir)
    injected.save(f"gradient_{grad_dir}_{ip.split('/')[-1].split('.')[0]}.png")


def inject_gradient(img_class, pixel_arr, start_color, end_color, grad_dir):
    p1, p2 = calc_gradient_poles(grad_dir, pixel_arr)
    print("Calculated poles for gradient:", p1, p2)
    img = paste_gradient(img_class, pixel_arr, p1, p2, start_color, end_color, grad_dir)
    return img


if __name__ == "__main__":
    gradient_single_change(
        (
            255,
            0,
            0,
        ),
        (
            0,
            0,
            255,
        ),
        "bottom-up",
    )
    # gradient_single_change((255,0,0,), (0,0,255,), "top-down")
    # gradient_single_change((255,0,0,), (0,0,255,), "left-right")
    # gradient_single_change((255,0,0,), (0,0,255,), "right-left")
    # gradient_single_change(
    #     (
    #         255,
    #         0,
    #         0,
    #     ),
    #     (
    #         0,
    #         0,
    #         255,
    #     ),
    #     "radial",
    # )
