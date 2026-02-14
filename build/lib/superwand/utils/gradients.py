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

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import math
from ..core.np_region_identifier import np_get_prominent_regions
import tempfile
import os


def twod_dist(p1, p2):
    spx, spy = p1
    epx, epy = p2
    return ((spx - epx) ** 2 + (spy - epy) ** 2) ** 0.5


def calc_gradient_poles(grad_kw, pixel_arr, img_size=None):
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

    if img_size:
        w, h = img_size
        match grad_kw:
            case "bottom-up":
                return (w / 2, h - 1), (w / 2, 0)
            case "top-down":
                return (w / 2, 0), (w / 2, h - 1)
            case "left-right":
                return (0, h / 2), (w - 1, h / 2)
            case "right-left":
                return (w - 1, h / 2), (0, h / 2)
            case "radial":
                return (w / 2, h / 2), (w - 1, h - 1)

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
    img_class,
    pixel_arr,
    start_pole,
    end_pole,
    start_color,
    end_color,
    grad_kw,
    polarity=0.5,
):
    draw = ImageDraw.Draw(img_class)
    spx, spy = start_pole
    epx, epy = end_pole
    s_r, s_g, s_b = start_color
    e_r, e_g, e_b = end_color

    # Midpoint/Bias logic
    # factor = factor ** p where p = log(0.5) / log(polarity)
    p = 1.0
    if polarity != 0.5 and polarity > 0 and polarity < 1:
        p = math.log(0.5) / math.log(polarity)

    match grad_kw:
        case "left-right" | "right-left":
            for x, y in pixel_arr:
                factor = (x - spx) / (epx - spx)
                factor = max(0, min(1, factor))
                if p != 1.0:
                    factor = factor**p
                r = int(s_r + (e_r - s_r) * factor)
                g = int(s_g + (e_g - s_g) * factor)
                b = int(s_b + (e_b - s_b) * factor)
                draw.point((x, y), fill=(r, g, b))
        case "bottom-up" | "top-down":
            for x, y in pixel_arr:
                factor = (y - spy) / (epy - spy)
                factor = max(0, min(1, factor))
                if p != 1.0:
                    factor = factor**p
                r = int(s_r + (e_r - s_r) * factor)
                g = int(s_g + (e_g - s_g) * factor)
                b = int(s_b + (e_b - s_b) * factor)
                draw.point((x, y), fill=(r, g, b))
        case "radial":
            max_radius = twod_dist(start_pole, end_pole)
            for x, y in pixel_arr:
                factor = twod_dist((x, y), start_pole) / max_radius
                factor = max(0, min(1, factor))
                if p != 1.0:
                    factor = factor**p
                r = int(s_r + (e_r - s_r) * factor)
                g = int(s_g + (e_g - s_g) * factor)
                b = int(s_b + (e_b - s_b) * factor)
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
    color1=None,
    color2=None,
    polarity=0.5,
) -> Image.Image:
    """
    Converts monocolor regions with directional gradient
    """
    intensity = 0.2
    if isinstance(img, str):
        img = Image.open(img).convert("RGB")

    img_size = img.size

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        img_path = tmp.name

    try:
        regions = np_get_prominent_regions(img_path)
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

    grad_kw = style
    if style == "auto" or style == "vertical":
        grad_kw = "top-down"
    elif style == "horizontal":
        grad_kw = "left-right"

    for color, pixels in regions.items():
        pixel_tuples = [[p[1], p[0]] for p in pixels]

        if color1 and color2:
            start_color = color1
            end_color = color2
        else:
            start_color = adjust_color(color, 1 + intensity)
            end_color = adjust_color(color, 1 - intensity)

        try:
            p1, p2 = calc_gradient_poles(grad_kw, pixel_tuples, img_size=img_size)
            img = paste_gradient(
                img,
                pixel_tuples,
                p1,
                p2,
                start_color,
                end_color,
                grad_kw,
                polarity=polarity,
            )
        except Exception as e:
            print(f"Failed to apply gradient to region {color}: {e}")
            continue

    return img
