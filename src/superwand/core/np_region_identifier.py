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
from .np_themes import np_get_prominent_colors, CORES_DOIS as CORES
from PIL import Image, ImageOps
import numpy as np
from sklearn.cluster import KMeans
from scipy.ndimage import binary_dilation, binary_closing
from collections import OrderedDict

MATCH_MODES = ("order", "luminance")


def np_id_regiones(img_path, target_color, tolerance=20, debug=False, img_array=None):
    if img_array is None:
        img = np.array(Image.open(img_path).convert("RGB"))
    else:
        img = img_array
    diff = np.sqrt(np.sum((img.astype(np.int32) - target_color) ** 2, axis=2))
    matches = np.argwhere(diff < tolerance)
    if debug:
        mask = np.zeros((*img.shape[:2], 4), dtype=np.uint8)
        mask[diff < tolerance] = (*target_color, 255)
        Image.fromarray(mask, "RGBA").show()
    return matches.tolist()


def np_get_prominent_regions(ip, number: int = 4, tolerance: int = 50, seed: int = 42):
    """
    Identifies prominent color regions using KMeans clustering.
    Returns an OrderedDict mapping cluster center RGB tuples to pixel indices
    ([row, col] arrays), largest region first. Every pixel is assigned to one
    of the k clusters. `tolerance` is kept for API compatibility and unused.
    """
    img = ip if isinstance(ip, Image.Image) else Image.open(ip)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img_array = np.array(img)
    h, w, _ = img_array.shape
    pixels = img_array.reshape(-1, 3)

    # Downsample for speed if image is large; seeded so results are reproducible
    rng = np.random.default_rng(seed)
    num_samples = min(len(pixels), 100000)
    indices = rng.choice(len(pixels), num_samples, replace=False)
    sample_pixels = pixels[indices]

    kmeans = KMeans(n_clusters=number, random_state=seed, n_init="auto").fit(
        sample_pixels
    )
    labels = np.array(kmeans.predict(pixels), dtype=int)
    centers = np.array(kmeans.cluster_centers_, dtype=int)
    # Sort clusters by size to maintain prominence order
    counts = np.bincount(labels, minlength=number)
    sorted_indices = np.argsort(-counts)

    color_regions = OrderedDict()
    labels_reshaped = labels.reshape((h, w))

    for i in sorted_indices:
        if counts[i] == 0:
            continue
        color_tuple = tuple(centers[i].tolist())
        color_regions[color_tuple] = np.argwhere(labels_reshaped == i)

    return color_regions


def extract_palette(ip, number: int = 4):
    """Returns the image's `number` dominant colors as RGB tuples, most prominent first."""
    return list(np_get_prominent_regions(ip, number=number).keys())


def luminance(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def match_palette(region_colors, palette, match="order"):
    """
    Assigns one palette color per region.
    - "order": region i (by prominence) gets palette[i], cycling if short.
    - "luminance": darkest region gets the darkest palette color, and so on,
      which preserves the image's light/shadow structure.
    """
    region_colors = list(region_colors)
    palette = [tuple(c) for c in palette]
    if not palette:
        raise ValueError("palette must contain at least one color")
    if match not in MATCH_MODES:
        raise ValueError(f"match must be one of {MATCH_MODES}, got {match!r}")

    n = len(region_colors)
    chosen = [palette[i % len(palette)] for i in range(n)]
    if match == "order":
        return chosen

    regions_by_lum = sorted(range(n), key=lambda i: luminance(region_colors[i]))
    colors_by_lum = sorted(chosen, key=luminance)
    assigned = [None] * n
    for region_idx, color in zip(regions_by_lum, colors_by_lum):
        assigned[region_idx] = color
    return assigned


def np_inject_2(
    image,
    pixel_arr,
    pixel,
    flood=False,
    gradient_style=None,
    gradient_polarity=0.5,
):
    gradient_intensity = 0.2
    if pixel is None:
        return image

    # Convert the image to a NumPy array
    arr = np.array(image)
    if arr.shape[-1] == 3:  # If the image is RGB, add an alpha channel
        arr = np.concatenate(
            [arr, np.full((*arr.shape[:2], 1), 255, dtype=np.uint8)], axis=-1
        )

    pixel_arr = np.array(pixel_arr)
    if len(pixel_arr) == 0:
        return image

    pixel_arr = pixel_arr.astype(int)
    height, width = arr.shape[:2]

    # pixel_arr rows are [y, x]
    y_coords = pixel_arr[:, 0]
    x_coords = pixel_arr[:, 1]

    valid_mask = (
        (y_coords >= 0) & (y_coords < height) & (x_coords >= 0) & (x_coords < width)
    )

    y_coords = y_coords[valid_mask]
    x_coords = x_coords[valid_mask]

    if len(y_coords) == 0:
        return image

    mask = np.zeros((height, width), dtype=bool)
    mask[y_coords, x_coords] = True

    if flood:
        # Close holes and dilate to "envelope"
        mask = binary_closing(mask, iterations=2)
        mask = binary_dilation(mask, iterations=3)

    # pixel can be a single RGB tuple or a list/tuple of two RGB tuples for gradients
    is_pair = isinstance(pixel[0], (list, tuple, np.ndarray))
    base_rgb = pixel[0] if is_pair else pixel

    target_pixel_rgba = np.array((*base_rgb[:3], 255), dtype=np.uint8)
    rows, cols = np.where(mask)
    arr[rows, cols, :] = target_pixel_rgba

    if gradient_style and gradient_style != "none":
        from ..utils.gradients import (
            adjust_color,
            blend_colors,
            calc_gradient_poles,
            gradient_factors,
            normalize_style,
        )

        style = normalize_style(gradient_style)
        if is_pair:
            start_color, end_color = pixel[0], pixel[1]
        else:
            start_color = adjust_color(base_rgb, 1 + gradient_intensity)
            end_color = adjust_color(base_rgb, 1 - gradient_intensity)

        try:
            # Poles span the whole image so neighbouring regions line up
            p1, p2 = calc_gradient_poles(style, None, img_size=(width, height))
            factor = gradient_factors(rows, cols, style, p1, p2, gradient_polarity)
            if factor is not None:
                arr[rows, cols, :3] = blend_colors(start_color, end_color, factor)
        except ValueError as e:
            print(f"Gradient failed: {e}")

    return Image.fromarray(arr, "RGBA")


def np_inject_theme_image(
    cpd,
    theme_rgbs,
    image,
    flood=False,
    gradient_styles=None,
    gradient_polarities=None,
):
    """Returns a PIL Image instead of saving to disk"""
    image = image.convert("RGB")
    for i, (color_key, target_color) in enumerate(zip(cpd.keys(), theme_rgbs)):
        # Handle cases where gradient_styles might be a single string or a list
        style = None
        if isinstance(gradient_styles, (list, tuple)):
            if i < len(gradient_styles):
                style = gradient_styles[i]
        else:
            style = gradient_styles

        polarity = 0.5
        if isinstance(gradient_polarities, (list, tuple)):
            if i < len(gradient_polarities):
                polarity = gradient_polarities[i]
        elif gradient_polarities is not None:
            polarity = gradient_polarities

        if polarity is None:
            polarity = 0.5

        # If a gradient is requested and we have multiple colors in the theme,
        # use the current color and the next color as start and end points.
        pixel_to_inject = target_color
        if style and style != "none" and len(theme_rgbs) > 1:
            # Only wrap if it's not already a gradient pair [c1, c2]
            is_already_gradient = (
                isinstance(target_color, (list, tuple))
                and len(target_color) == 2
                and isinstance(target_color[0], (list, tuple))
            )
            if not is_already_gradient and target_color is not None:
                next_color = theme_rgbs[(i + 1) % len(theme_rgbs)]
                if next_color is not None:
                    pixel_to_inject = (target_color, next_color)

        image = np_inject_2(
            image,
            cpd[color_key],
            pixel_to_inject,
            flood=flood,
            gradient_style=style,
            gradient_polarity=polarity,
        )
    return image


def resolve_theme(theme):
    """A theme is either a built-in theme name or a sequence of RGB tuples."""
    if isinstance(theme, str):
        if theme not in CORES:
            raise ValueError(
                f"Unknown theme {theme!r}. Available: {', '.join(CORES)}"
            )
        return list(CORES[theme])
    return [tuple(c) for c in theme]


def np_inject_theme(
    cpd,
    theme_name,
    image_path,
    number=4,
    flood=False,
    gradient_styles=None,
    gradient_polarities=None,
    output_dir=".",
    match="order",
    palette=None,
):
    """
    Rethemes image_path with a built-in theme (or an explicit `palette`, in
    which case theme_name only labels the output) and saves
    <name>_<theme_name>.png in output_dir. Returns the saved path.
    """
    theme_rgbs = match_palette(
        list(cpd.keys())[:number], resolve_theme(palette if palette is not None else theme_name), match
    )
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image).convert("RGB")
    image = np_inject_theme_image(
        cpd,
        theme_rgbs,
        image,
        flood=flood,
        gradient_styles=gradient_styles,
        gradient_polarities=gradient_polarities,
    )
    stem = os.path.splitext(os.path.basename(image_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{stem}_{theme_name}.png")
    image.save(out_path)
    return out_path
