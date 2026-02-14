from .__np_color_themes__ import np_get_prominent_colors, CORES_DOIS as CORES
from PIL import Image
import secrets
import numpy as np
from sklearn.cluster import KMeans
from scipy.ndimage import binary_dilation, binary_closing
from collections import OrderedDict


def np_id_regiones(img_path, target_color, tolerance=20, debug=False, img_array=None):
    if img_array is None:
        img = np.array(Image.open(img_path).convert("RGB"))
    else:
        img = img_array
    diff = np.sqrt(np.sum((img - target_color) ** 2, axis=2))
    matches = np.argwhere(diff < tolerance)
    if debug:
        mask = np.zeros((*img.shape[:2], 4), dtype=np.uint8)
        mask[diff < tolerance] = (*target_color, 255)
        Image.fromarray(mask, "RGBA").show()
    return matches.tolist()


def np_get_prominent_regions(ip: str, number: int = 4, tolerance: int = 50):
    """
    Identifies prominent color regions using KMeans clustering.
    Returns an OrderedDict mapping cluster center RGB tuples to pixel indices.
    Every pixel is assigned to one of the k clusters.
    """
    img = Image.open(ip)
    from PIL import ImageOps

    img = ImageOps.exif_transpose(img).convert("RGB")
    img_array = np.array(img)
    h, w, _ = img_array.shape
    pixels = img_array.reshape(-1, 3)

    # Use KMeans to find 'number' clusters as original values
    # Downsample for speed if image is large
    num_samples = min(len(pixels), 100000)
    indices = np.random.choice(len(pixels), num_samples, replace=False)
    sample_pixels = pixels[indices]

    kmeans = KMeans(n_clusters=number, random_state=42, n_init="auto").fit(
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
        color_tuple = tuple(centers[i].tolist())
        region_indices = np.argwhere(labels_reshaped == i)
        color_regions[color_tuple] = region_indices

    return color_regions


def np_inject_2(
    image, pixel_arr, pixel, flood=False, gradient_style=None, gradient_intensity=0.2
):
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

    # original pixel_arr from np_id_regiones is [y, x]
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
    if isinstance(pixel[0], (list, tuple, np.ndarray)):
        start_rgb, end_rgb = pixel[0], pixel[1]
        base_rgb = start_rgb  # fallback for non-gradient use
    else:
        start_rgb = None
        end_rgb = None
        base_rgb = pixel

    target_pixel_rgba = np.array((*base_rgb, 255), dtype=np.uint8)
    rows, cols = np.where(mask)

    if gradient_style and gradient_style != "none":
        # Apply gradient logic
        from .gradients import twod_dist, calc_gradient_poles, adjust_color

        # Map UI styles to internal styles
        style_map = {
            "vertical": "top-down",
            "horizontal": "left-right",
            "auto": "top-down",
        }
        style = style_map.get(gradient_style, gradient_style)

        if len(rows) > 0:
            try:
                # Use global image boundaries for poles if style is provided
                poles = calc_gradient_poles(style, None, img_size=(width, height))
                if poles is None:
                    arr[rows, cols, :] = target_pixel_rgba
                else:
                    p1, p2 = poles
                    if p1 is None or p2 is None:
                        arr[rows, cols, :] = target_pixel_rgba
                    else:
                        if isinstance(pixel[0], (list, tuple, np.ndarray)):
                            start_color = pixel[0]
                            end_color = pixel[1]
                        else:
                            start_color = adjust_color(base_rgb, 1 + gradient_intensity)
                            end_color = adjust_color(base_rgb, 1 - gradient_intensity)

                        if style in ["left-right", "right-left"]:
                            spx, epx = float(p1[0]), float(p2[0])
                            if abs(epx - spx) < 1e-6:
                                arr[rows, cols, :] = target_pixel_rgba
                            else:
                                factor = (cols.astype(np.float64) - spx) / (epx - spx)
                                factor = np.clip(factor, 0, 1)[:, np.newaxis]
                                sc = np.array(start_color, dtype=np.float64)
                                ec = np.array(end_color, dtype=np.float64)
                                colors = sc + (ec - sc) * factor
                                arr[rows, cols, :3] = colors.astype(np.uint8)
                                arr[rows, cols, 3] = 255

                        elif style in ["top-down", "bottom-up"]:
                            spy, epy = float(p1[1]), float(p2[1])
                            if abs(epy - spy) < 1e-6:
                                arr[rows, cols, :] = target_pixel_rgba
                            else:
                                factor = (rows.astype(np.float64) - spy) / (epy - spy)
                                factor = np.clip(factor, 0, 1)[:, np.newaxis]
                                sc = np.array(start_color, dtype=np.float64)
                                ec = np.array(end_color, dtype=np.float64)
                                colors = sc + (ec - sc) * factor
                                arr[rows, cols, :3] = colors.astype(np.uint8)
                                arr[rows, cols, 3] = 255

                        elif style == "radial":
                            center = np.array(p1, dtype=np.float64)
                            max_dist = float(twod_dist(p1, p2))
                            if max_dist < 1e-6:
                                arr[rows, cols, :] = target_pixel_rgba
                            else:
                                pts = np.column_stack((cols, rows)).astype(np.float64)
                                dists = np.sqrt(np.sum((pts - center) ** 2, axis=1))
                                factor = (dists / max_dist)[:, np.newaxis]
                                factor = np.clip(factor, 0, 1)
                                sc = np.array(start_color, dtype=np.float64)
                                ec = np.array(end_color, dtype=np.float64)
                                colors = sc + (ec - sc) * factor
                                arr[rows, cols, :3] = colors.astype(np.uint8)
                                arr[rows, cols, 3] = 255
                        else:
                            arr[rows, cols, :] = target_pixel_rgba
            except Exception as e:
                print(f"Gradient failed: {e}")
                arr[rows, cols, :] = target_pixel_rgba
    else:
        if len(rows) > 0:
            arr[rows, cols, :] = target_pixel_rgba

    return Image.fromarray(arr, "RGBA")


def np_inject_theme_image(
    cpd,
    theme_rgbs,
    image,
    flood=False,
    gradient_styles=None,
    gradient_intensities=None,
):
    """Returns a PIL Image instead of saving to disk"""
    image = image.convert("RGB")
    for i, (color_key, target_pixel) in enumerate(zip(cpd.keys(), theme_rgbs)):
        # Handle cases where gradient_styles might be a single string or a list
        style = None
        if isinstance(gradient_styles, (list, tuple)):
            if i < len(gradient_styles):
                style = gradient_styles[i]
        else:
            style = gradient_styles

        intensity = 0.2
        if isinstance(gradient_intensities, (list, tuple)):
            if i < len(gradient_intensities):
                intensity = gradient_intensities[i]
        elif gradient_intensities is not None:
            intensity = gradient_intensities

        if intensity is None:
            intensity = 0.2

        image = np_inject_2(
            image,
            cpd[color_key],
            target_pixel,
            flood=flood,
            gradient_style=style,
            gradient_intensity=intensity,
        )
    return image


def np_inject_theme(
    cpd,
    theme_name,
    image_path,
    number=4,
    flood=False,
    gradient_styles=None,
    gradient_intensities=None,
):
    # fmt : off
    theme_rgbs = (c := CORES[theme_name])[: min(number, len(c))] + [
        secrets.choice(c) for _ in range(max(number - len(c), 0))
    ]
    # fmt : on
    image = Image.open(image_path).convert("RGB")
    image = np_inject_theme_image(
        cpd,
        theme_rgbs,
        image,
        flood=flood,
        gradient_styles=gradient_styles,
        gradient_intensities=gradient_intensities,
    )
    image.save(f"{image_path.split('/')[-1].split('.')[0]}_{theme_name}.png")


class JHsuperwand:
    # fmt: off
    def __init__(_s, ip, slowww = 4):_s.np_color_pix_dict, _s.slowww = (np_get_prominent_regions(ip,number = slowww), slowww,)
    # fmt: on

    def superwand_jh(
        _s,
        theme_name,
        ip,
        flood=False,
        gradient_styles=None,
        gradient_intensities=None,
    ):
        np_inject_theme(
            _s.np_color_pix_dict,
            theme_name,
            ip,
            number=_s.slowww,
            flood=flood,
            gradient_styles=gradient_styles,
            gradient_intensities=gradient_intensities,
        )
