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

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import math
from .np_region_identifier import np_get_prominent_regions
import tempfile
import os


def twod_dist(p1, p2):
    spx, spy = p1
    epx, epy = p2
    return ((spx - epx) ** 2 + (spy - epy) ** 2) ** 0.5


def calc_gradient_poles(grad_kw, pixel_arr):
    print("processing", grad_kw)

    def calculate_distance(point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def farthest_point_from_center(_pixel_arr, center):
        farthest_point = None
        max_distance = float("-inf")
        for point in _pixel_arr:
            distance = calculate_distance(point, center)
            if distance > max_distance:
                max_distance = distance
                farthest_point = point
        return farthest_point

    match grad_kw:
        case "bottom-up":
            mid_x = (
                min([xy[0] for xy in pixel_arr]) + max([xy[0] for xy in pixel_arr])
            ) / 2
            min_y = min([xy[1] for xy in pixel_arr])
            max_y = max([xy[1] for xy in pixel_arr])
            return (mid_x, max_y), (mid_x, min_y)
        case "top-down":
            mid_x = (
                min([xy[0] for xy in pixel_arr]) + max([xy[0] for xy in pixel_arr])
            ) / 2
            min_y = min([xy[1] for xy in pixel_arr])
            max_y = max([xy[1] for xy in pixel_arr])
            return (mid_x, min_y), (mid_x, max_y)
        case "left-right":
            mid_y = (
                min([xy[1] for xy in pixel_arr]) + max([xy[1] for xy in pixel_arr])
            ) / 2
            min_x = min([xy[0] for xy in pixel_arr])
            max_x = max([xy[0] for xy in pixel_arr])
            return (min_x, mid_y), (max_x, mid_y)
        case "right-left":
            mid_y = (
                min([xy[1] for xy in pixel_arr]) + max([xy[1] for xy in pixel_arr])
            ) / 2
            min_x = min([xy[0] for xy in pixel_arr])
            max_x = max([xy[0] for xy in pixel_arr])
            return (max_x, mid_y), (min_x, mid_y)
        case "radial":
            sum_x = sum(point[0] for point in pixel_arr)
            sum_y = sum(point[1] for point in pixel_arr)
            center_x = sum_x / len(pixel_arr)
            center_y = sum_y / len(pixel_arr)
            center_xy = (center_x, center_y)
            farthest_point = farthest_point_from_center(pixel_arr, center_xy)
            return center_xy, farthest_point
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")


def paste_gradient(
    img_class, pixel_arr, start_pole, end_pole, start_color, end_color, grad_kw
):
    draw = ImageDraw.Draw(img_class)
    spx, spy = start_pole
    epx, epy = end_pole
    s_r, s_g, s_b = start_color
    e_r, e_g, e_b = end_color
    match grad_kw:
        case "left-right" | "right-left":
            for x, y in pixel_arr:
                r = int(s_r + (e_r - s_r) * ((x - spx) / (epx - spx)))
                g = int(s_g + (e_g - s_g) * ((x - spx) / (epx - spx)))
                b = int(s_b + (e_b - s_b) * ((x - spx) / (epx - spx)))
                draw.point((x, y), fill=(r, g, b))
        case "bottom-up" | "top-down":
            for x, y in pixel_arr:
                r = int(e_r + (s_r - e_r) * ((y - spy) / (epy - spy)))
                g = int(e_g + (s_g - e_g) * ((y - spy) / (epy - spy)))
                b = int(e_b + (s_b - e_b) * ((y - spy) / (epy - spy)))
                draw.point((x, y), fill=(r, g, b))
        case "radial":
            max_radius = twod_dist(start_pole, end_pole)
            for x, y in pixel_arr:
                r = int(
                    s_r
                    + (e_r - s_r)
                    * twod_dist(
                        (
                            x,
                            y,
                        ),
                        start_pole,
                    )
                    / max_radius
                )
                g = int(
                    s_g
                    + (e_g - s_g)
                    * twod_dist(
                        (
                            x,
                            y,
                        ),
                        start_pole,
                    )
                    / max_radius
                )
                b = int(
                    s_b
                    + (e_b - s_b)
                    * twod_dist(
                        (
                            x,
                            y,
                        ),
                        start_pole,
                    )
                    / max_radius
                )
                draw.point((x, y), fill=(r, g, b))
    return img_class


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def adjust_color(color, factor):
    r, g, b = color
    return (
        clamp(int(r * factor), 0, 255),
        clamp(int(g * factor), 0, 255),
        clamp(int(b * factor), 0, 255),
    )


def gradient_enforce(
    img: Image.Image,
    style="auto",
    completeness="auto",
    opacity="auto",
    intensity=0.2,
) -> Image.Image:
    """
    Converts monocolor regionswith directional gradient

    style :
    ~ direction of gradients
            -> auto, best guess based on boosting
            -> vertical
            -> horizontal

    completeness :
    ~impacted regions
            -> aggressive, all colors
            -> auto, most impact
            -> filter, color or set of colors

    opacity :
    ~makes achieve minimum opacity value in region
            -> clamp {0, 1}
            -> failsafe rounds

    intensity :
    ~dramaticism of the gradient (0.0 to 1.0)
    """
    # ...
    # Apply gradients
    for color, pixels in regions.items():
        # ...
        # Create gradient colors based on original color
        # Make one end lighter and one end darker
        start_color = adjust_color(color, 1 + intensity)
        end_color = adjust_color(color, 1 - intensity)

        # Calculate poles
        try:
            p1, p2 = calc_gradient_poles(grad_kw, pixel_tuples)

            # Apply gradient
            img = paste_gradient(
                img, pixel_tuples, p1, p2, start_color, end_color, grad_kw
            )
        except Exception as e:
            print(f"Failed to apply gradient to region {color}: {e}")
            continue

    return img
