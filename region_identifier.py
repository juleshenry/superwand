from collections import OrderedDict

import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial.distance import euclidean
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb, rgb_to_name

from __color_themes__ import color_themes, get_prominent_colors


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
            # if (r,g,b,) == (0,0,0,):
            #     print(r,g,b);1/0
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


def get_prominent_regions(ip, number=4):
    target_colors = get_prominent_colors(ip, number=number)
    color_regions = OrderedDict()
    for color in target_colors:
        color_regions[color] = identify_regions(ip, color, tolerance=50)
    return color_regions


def inject_theme(cpd, theme_name, image_path, gradient_direction="vertical"):
    print(theme_name)
    theme_rgbs = color_themes[theme_name]
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    start_color, end_color = theme_rgbs[0], theme_rgbs[-1]
    for cpd_theme in zip(cpd, theme_rgbs):
        for xy in cpd[cpd_theme[0]]:
            x, y = xy
            if gradient_direction == "vertical":
                gradient = ImageDraw.LinearGradient((0, 0, 0, image.height), start_color, end_color)
                draw.rectangle([(x, y), (x + 1, y + 1)], fill=gradient)
            elif gradient_direction == "left-right":
                gradient = ImageDraw.LinearGradient((0, 0, image.width, 0), start_color, end_color)
                draw.rectangle([(x, y), (x + 1, y + 1)], fill=gradient)
            elif gradient_direction == "right-left":
                gradient = ImageDraw.LinearGradient((image.width, 0, 0, 0), start_color, end_color)
                draw.rectangle([(x, y), (x + 1, y + 1)], fill=gradient)
            elif gradient_direction == "bottom-down":
                gradient = ImageDraw.LinearGradient((0, image.height, 0, 0), start_color, end_color)
                draw.rectangle([(x, y), (x + 1, y + 1)], fill=gradient)
            elif gradient_direction == "radial":
                gradient = ImageDraw.RadialGradient((image.width//2, image.height//2), start_color, end_color)
                draw.rectangle([(x, y), (x + 1, y + 1)], fill=gradient)
    image.save(f"{theme_name}_{image_path.split('/')[-1].split('.')[0]}.png")


if __name__ == "__main__":
    ip = "examples/images/charizard.png"
    color_pix_dict = get_prominent_regions(ip)
    for theme_name in color_themes:
        if theme_name != "Tropical":
            continue
        else:
            inject_theme(color_pix_dict, theme_name, ip)
        # break
