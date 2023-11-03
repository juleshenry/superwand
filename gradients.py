import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


def twod_dist(p1, p2):
    spx, spy = p1
    epx, epy = p2
    return ((spx - epx) ** 2 + (spy - epy) ** 2) ** 0.5


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
