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

import math
import numpy as np
from PIL import Image
from ..core.np_region_identifier import np_get_prominent_regions

# UI / CLI aliases for the canonical gradient directions
STYLE_ALIASES = {
    "auto": "top-down",
    "vertical": "top-down",
    "horizontal": "left-right",
}


def normalize_style(style):
    return STYLE_ALIASES.get(style, style)


def twod_dist(p1, p2):
    spx, spy = p1
    epx, epy = p2
    return ((spx - epx) ** 2 + (spy - epy) ** 2) ** 0.5


def calc_gradient_poles(grad_kw, pixel_arr, img_size=None):
    """
    Returns (start_pole, end_pole) as (x, y) points. With img_size the poles
    span the whole image; otherwise they span the bounding box of pixel_arr
    (a sequence of [x, y] points).
    """
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
            case _:
                raise ValueError(f"Unsupported gradient keyword {grad_kw}")

    pts = np.asarray(pixel_arr, dtype=np.float64).reshape(-1, 2)
    xs, ys = pts[:, 0], pts[:, 1]
    match grad_kw:
        case "bottom-up":
            mid_x = (xs.min() + xs.max()) / 2
            return (mid_x, ys.max()), (mid_x, ys.min())
        case "top-down":
            mid_x = (xs.min() + xs.max()) / 2
            return (mid_x, ys.min()), (mid_x, ys.max())
        case "left-right":
            mid_y = (ys.min() + ys.max()) / 2
            return (xs.min(), mid_y), (xs.max(), mid_y)
        case "right-left":
            mid_y = (ys.min() + ys.max()) / 2
            return (xs.max(), mid_y), (xs.min(), mid_y)
        case "radial":
            center = pts.mean(axis=0)
            farthest = pts[np.argmax(np.hypot(xs - center[0], ys - center[1]))]
            return tuple(center.tolist()), tuple(farthest.tolist())
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")


def polarity_exponent(polarity):
    """
    Exponent p such that factor ** p == 0.5 when factor == polarity, i.e.
    polarity is how far along the gradient the 50/50 blend lands.
    """
    # Clamp so polarity works even when very close to 0 or 1
    safe_polarity = max(0.001, min(0.999, polarity))
    if safe_polarity == 0.5:
        return 1.0
    return math.log(0.5) / math.log(safe_polarity)


def gradient_factors(rows, cols, grad_kw, start_pole, end_pole, polarity=0.5):
    """
    Vectorized position of each (row, col) pixel along the gradient, in [0, 1].
    Returns None when the poles are degenerate (zero-length gradient).
    """
    rows = np.asarray(rows, dtype=np.float64)
    cols = np.asarray(cols, dtype=np.float64)
    spx, spy = float(start_pole[0]), float(start_pole[1])
    epx, epy = float(end_pole[0]), float(end_pole[1])

    match grad_kw:
        case "left-right" | "right-left":
            if abs(epx - spx) < 1e-6:
                return None
            factor = (cols - spx) / (epx - spx)
        case "top-down" | "bottom-up":
            if abs(epy - spy) < 1e-6:
                return None
            factor = (rows - spy) / (epy - spy)
        case "radial":
            max_dist = twod_dist(start_pole, end_pole)
            if max_dist < 1e-6:
                return None
            factor = np.hypot(cols - spx, rows - spy) / max_dist
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")

    factor = np.clip(factor, 0, 1)
    p = polarity_exponent(polarity)
    return factor**p if p != 1.0 else factor


def blend_colors(start_color, end_color, factor):
    """Linear blend per pixel; returns an (N, 3) uint8 array."""
    sc = np.asarray(start_color, dtype=np.float64)[:3]
    ec = np.asarray(end_color, dtype=np.float64)[:3]
    return (sc + (ec - sc) * factor[:, np.newaxis]).astype(np.uint8)


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
    """Paints a gradient over pixel_arr ([x, y] points) and returns the new image."""
    pts = np.asarray(pixel_arr, dtype=int).reshape(-1, 2)
    if len(pts) == 0:
        return img_class
    cols, rows = pts[:, 0], pts[:, 1]
    factor = gradient_factors(rows, cols, grad_kw, start_pole, end_pole, polarity)
    if factor is None:
        return img_class

    arr = np.array(img_class)
    arr[rows, cols, :3] = blend_colors(start_color, end_color, factor)
    return Image.fromarray(arr, img_class.mode)


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def adjust_color(color, factor):
    r, g, b = color[:3]
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
    number=4,
) -> Image.Image:
    """
    Converts monocolor regions with directional gradient
    """
    intensity = 0.2
    if isinstance(img, str):
        img = Image.open(img)
    img = img.convert("RGB")

    grad_kw = normalize_style(style)
    p1, p2 = calc_gradient_poles(grad_kw, None, img_size=img.size)

    regions = np_get_prominent_regions(img, number=number)
    arr = np.array(img)
    for color, pixels in regions.items():
        if color1 and color2:
            start_color, end_color = color1, color2
        else:
            start_color = adjust_color(color, 1 + intensity)
            end_color = adjust_color(color, 1 - intensity)

        rows, cols = pixels[:, 0], pixels[:, 1]
        factor = gradient_factors(rows, cols, grad_kw, p1, p2, polarity)
        if factor is None:
            continue
        arr[rows, cols] = blend_colors(start_color, end_color, factor)

    return Image.fromarray(arr, "RGB")
