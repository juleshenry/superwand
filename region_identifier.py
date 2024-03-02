from __color_themes__ import get_prominent_colors, color_themes
from PIL import Image
import numpy as np
from webcolors import rgb_to_name, hex_to_rgb, CSS3_HEX_TO_NAMES
from collections import OrderedDict
from tqdm import tqdm

def rgb_distance(color1, color2):
    return np.sqrt(np.sum((color1 - color2) ** 2))

def identify_regions(image_path, target_color, tolerance=20, debug=False):
    # Convert target_color to RGB tuple if it's a string or hex
    if isinstance(target_color, str):
        target_color = hex_to_rgb(target_color)
    elif isinstance(target_color, tuple):
        target_color = np.array(target_color)

    # Open the image
    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    # Convert target_color to numpy array for faster computation
    target_color = np.array(target_color)

    matching_pixels = []


    for y in tqdm(range(height)):
        for x in range(width):
            # Get the RGB values of the current pixel
            pixel_color = np.array(image.getpixel((x, y)))

            # Calculate the distance between the target color and the current pixel color
            distance = rgb_distance(target_color, pixel_color)

            if distance < tolerance:
                matching_pixels.append([x, y])
   
    region_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for x, y in matching_pixels:
        region_image.putpixel((x, y), (*target_color, 255))

    if debug:
        region_image.show()

    return matching_pixels


def get_prominent_regions(ip, number=4):
    target_colors = get_prominent_colors(ip, number=number)
    color_regions = OrderedDict()
    for color in target_colors:
        color_regions[color] = identify_regions(ip, color, tolerance=50)
    return color_regions


def inject(img, pixel_arr, pixel):
    for xy in pixel_arr:
        x, y = xy
        img.putpixel((x, y), (*pixel, 255))
    return img


def inject_theme(cpd, theme_name, image_path):
    theme_rgbs = color_themes[theme_name]
    image = Image.open(image_path).convert("RGB")
    for cpd_theme in zip(cpd, theme_rgbs):
        image = inject(image, cpd[cpd_theme[0]], cpd_theme[1])
    image.save(f"{image_path.split('/')[-1].split('.')[0]}_{theme_name}.png")


if __name__ == "__main__":
    ip = "examples/images/mantis_shrimp.jpeg"
    color_pix_dict = get_prominent_regions(ip)
    for theme_name in color_themes:
        if theme_name != "Tropical":
            continue
        else:
            inject_theme(color_pix_dict, theme_name, ip)
        # break
