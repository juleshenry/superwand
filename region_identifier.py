from __color_themes__ import get_prominent_colors, color_themes
from PIL import Image
import numpy as np
from scipy.spatial.distance import euclidean
from webcolors import rgb_to_name, hex_to_rgb, CSS3_HEX_TO_NAMES
from collections import OrderedDict

def identify_regions(image_path, target_color, tolerance=20, debug=False):
    # Convert target_color to RGB tuple if it's a string or hex
    # Open the image
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    matching_pixels = []
    for y in range(height):
        for x in range(width):
            # Get the RGB values of the current pixel
            r, g, b = image.getpixel(
                (
                    x,
                    y,
                )
            )
            # print(r,g,b)
            if (
                euclidean(
                    target_color,
                    (
                        r,
                        g,
                        b,
                    ),
                )
                < tolerance
            ):
                matching_pixels.append([x, y])

    region_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for x, y in matching_pixels:
        region_image.putpixel((x, y), (*target_color, 255))
    if debug:
        region_image.show()
    return matching_pixels


def get_prominent_regions(ip, number = 4):
    target_colors = get_prominent_colors(ip, number=number)
    color_regions = OrderedDict()
    for color in target_colors:
        color_regions[color] = identify_regions(ip, color, tolerance=50)
    return color_regions


def inject_theme(cpd, theme):
    for c in zip(cpd, theme):
        print(c)

if __name__ == "__main__":
    ip = "examples/images/mantis_shrimp.jpeg"
    ip = "examples/images/pikachu_sprite.png"
    color_pix_dict = get_prominent_regions(ip)
    color_theme = [x for x in color_themes['Arctic'][0]]
    inject_theme(color_pix_dict, color_theme)
    