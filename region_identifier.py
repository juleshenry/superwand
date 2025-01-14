from __color_themes__ import get_prominent_colors, np_get_prominent_colors, color_themes
from PIL import Image
import numpy as np
import datetime as dt
from scipy.spatial.distance import euclidean
# from webcolors import rgb_to_name, hex_to_rgb
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
    print('***'*10)
    print("Vanilla ----->")
    print(s:=(o:=lambda:dt.datetime.now())())
    color_pix_dict = get_prominent_regions(ip)
    for theme_name in color_themes:
        if theme_name != "Tropical":
            continue
        else:
            inject_theme(color_pix_dict, theme_name, ip)
    print(o() - s)
    print('***'*10)
