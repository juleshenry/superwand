from __np_color_themes__ import np_get_prominent_colors, CORES
from PIL import Image
import numpy as np
import datetime as dt
from scipy.spatial.distance import euclidean
# from webcolors import rgb_to_name, hex_to_rgb
from collections import OrderedDict

    
def np_id_regiones(img_path, target_color, tolerance=20, debug=False):
    img = np.array(Image.open(img_path).convert('RGB'))
    diff = np.sqrt(np.sum((img - target_color) ** 2, axis=2))
    matches = np.argwhere(diff < tolerance)
    if debug:
        mask = np.zeros((*img.shape[:2], 4), dtype=np.uint8)
        mask[diff < tolerance] = (*target_color, 255)
        Image.fromarray(mask, 'RGBA').show()
    return matches.tolist()

def np_get_prominent_regions(ip, number=4):
    target_colors = np_get_prominent_colors(ip, number=number)
    color_regions = OrderedDict()
    for color in target_colors:
        # Convert color to tuple before using as a dictionary key
        color_tuple = tuple(color)
        color_regions[color_tuple] = np_id_regiones(ip, color, tolerance=50)
    return color_regions

def np_inject(image, pixel_arr, pixel):
    # Convert the image to a NumPy array
    arr = np.array(image)

    # Ensure the array has 4 channels (RGBA)
    if arr.shape[-1] == 3:  # If the image is RGB, add an alpha channel
        arr = np.concatenate(
            [arr, np.full((*arr.shape[:2], 1), 255, dtype=np.uint8)], axis=-1
        )

    # Convert pixel_arr to a NumPy array if it isn't already
    pixel_arr = np.array(pixel_arr)

    # Ensure pixel_arr contains valid integer indices
    pixel_arr = pixel_arr.astype(int)

    # Bounds-check to remove out-of-bound indices
    height, width = arr.shape[:2]
    valid_mask = (pixel_arr[:, 1] < height) & (pixel_arr[:, 0] < width)
    pixel_arr = pixel_arr[valid_mask]

    # Correct the coordinate order for (y, x) indexing
    arr[pixel_arr[:, 1], pixel_arr[:, 0]] = (*pixel, 255)

    # Convert the updated array back to an image
    return Image.fromarray(arr, 'RGBA')

def np_inject(image, pixel_arr, pixel):
    # Convert the image to a NumPy array
    arr = np.array(image)

    # Ensure the array has 4 channels (RGBA)
    if arr.shape[-1] == 3:  # If the image is RGB, add an alpha channel
        arr = np.concatenate(
            [arr, np.full((*arr.shape[:2], 1), 255, dtype=np.uint8)], axis=-1
        )

    # Convert pixel_arr to a NumPy array if it isn't already
    pixel_arr = np.array(pixel_arr)

    # Ensure pixel_arr contains valid integer indices
    pixel_arr = pixel_arr.astype(int)

    # Bounds-check to remove out-of-bound indices
    height, width = arr.shape[:2]
    valid_mask = (pixel_arr[:, 1] < height) & (pixel_arr[:, 0] < width)
    pixel_arr = pixel_arr[valid_mask]

    # Assign the new pixel values
    arr[pixel_arr[:, 1], pixel_arr[:, 0]] = (*pixel, 255)

    # Convert the updated array back to an image
    return Image.fromarray(arr, 'RGBA')

def np_inject_theme(cpd, theme_name, image_path):
    theme_rgbs = CORES[theme_name]
    image = Image.open(image_path).convert("RGB")
    for cpd_theme in zip(cpd, theme_rgbs):
        image = np_inject(image, cpd[cpd_theme[0]], cpd_theme[1])
    image.save(f"{image_path.split('/')[-1].split('.')[0]}_{theme_name}.png")


if __name__ == "__main__":
    ip = "examples/images/mantis_shrimp.jpeg"
    print("NP ----->")
    print(s:=(o:=lambda:dt.datetime.now())())
    np_color_pix_dict = np_get_prominent_regions(ip)
    for theme_name in CORES:
        if theme_name != "Tropical":
            continue
        else:
            np_inject_theme(np_color_pix_dict, theme_name, ip)
    print(o() - s)

    print('***'*10)
    