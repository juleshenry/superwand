from __np_color_themes__ import np_get_prominent_colors, CORES_DOIS as CORES
from PIL import Image
import numpy as np
import datetime as dt
from scipy.spatial.distance import euclidean

# from webcolors import rgb_to_name, hex_to_rgb
from collections import OrderedDict


def np_id_regiones(img_path, target_color, tolerance=20, debug=False):
    img = np.array(Image.open(img_path).convert("RGB"))
    diff = np.sqrt(np.sum((img - target_color) ** 2, axis=2))
    matches = np.argwhere(diff < tolerance)
    if debug:
        mask = np.zeros((*img.shape[:2], 4), dtype=np.uint8)
        mask[diff < tolerance] = (*target_color, 255)
        Image.fromarray(mask, "RGBA").show()
    return matches.tolist()


def np_get_prominent_regions(ip: str, number: int = 4):
    """
    image path
    custom color
    """
    target_colors = np_get_prominent_colors(ip, number=number)
    color_regions = OrderedDict()
    for color in target_colors:
        # Convert color to tuple before using as a dictionary key
        color_tuple = tuple(color)
        color_regions[color_tuple] = np_id_regiones(ip, color, tolerance=50)
    return color_regions


def np_inject_2(image, pixel_arr, pixel):
    # Convert the image to a NumPy array
    arr = np.array(image)
    if arr.shape[-1] == 3:  # If the image is RGB, add an alpha channel
        arr = np.concatenate(
            [arr, np.full((*arr.shape[:2], 1), 255, dtype=np.uint8)], axis=-1
        )
    pixel_arr = np.array(pixel_arr)
    pixel_arr = pixel_arr.astype(int)
    pixel_arr = pixel_arr[:, [1, 0]]  # Swap the columns (x, y) to (y, x)
    height, width = arr.shape[:2]
    valid_mask = (pixel_arr[:, 1] < height) & (pixel_arr[:, 0] < width)
    pixel_arr = pixel_arr[valid_mask]
    arr[pixel_arr[:, 1], pixel_arr[:, 0]] = (*pixel, 255)
    return Image.fromarray(arr, "RGBA")


def np_inject_theme(cpd, theme_name, image_path):
    theme_rgbs = CORES[theme_name]
    image = Image.open(image_path).convert("RGB")
    for cpd_theme in zip(cpd, theme_rgbs):
        print(cpd_theme)
        image = np_inject_2(image, cpd[cpd_theme[0]], cpd_theme[1])
    image.save(f"{image_path.split('/')[-1].split('.')[0]}_{theme_name}.png")


class JHsuperwand:
    # fmt: off
    def __init__(_s, ip, slowww = 4):_s.np_color_pix_dict, _s.slowww = (np_get_prominent_regions(ip,number = slowww), slowww,)
    # fmt: on

    def superwand_jh(_s, theme_name, ip):
        np_inject_theme(_s.np_color_pix_dict, theme_name, ip)


if __name__ == "__main__":
    ip = "examples/images/mantis_shrimp.jpeg"
    print("NP ----->")
    print(s := (o := lambda: dt.datetime.now())())
    jh = JHsuperwand(ip, slowww = 4)
    for theme_name in CORES:
        if theme_name != "Safari":
            continue
        else:
            jh.superwand_jh(theme_name, ip)
    print(o() - s)

    print("***" * 10)
