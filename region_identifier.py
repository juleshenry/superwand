from __color_themes__ import get_prominent_colors
from PIL import Image
import numpy as np
from scipy.spatial.distance import euclidean
from webcolors import rgb_to_name



def cool_rgb_to_name(color):
    def find_named_color(rgb):
        try:
            color_name = rgb_to_name(rgb)
            return color_name
        except ValueError:
            return None

    def adjust_rgb(rgb, index, increment):
        new_rgb = list(rgb)
        new_rgb[index] += increment
        return tuple(new_rgb)

    def find_closest_named_color(start_rgb):
        current_rgb = start_rgb
        increment = 1

        while True:
            color_name = find_named_color(current_rgb)
            
            if color_name is not None:
                return color_name

            for i in range(3):
                adjusted_rgb = adjust_rgb(current_rgb, i, increment)
                color_name = find_named_color(adjusted_rgb)

                if color_name is not None:
                    return color_name

                adjusted_rgb = adjust_rgb(current_rgb, i, -increment)
                color_name = find_named_color(adjusted_rgb)

                if color_name is not None:
                    return color_name

            increment += 1

    return find_closest_named_color(color)

def identify_regions(image_path, target_color, tolerance=20,debug=False):
    # Convert target_color to RGB tuple if it's a string or hex
    # Open the image
    image = Image.open(image_path).convert('RGB')
    width, height = image.size
    matching_pixels = []
    for y in range(height):
        for x in range(width):
            # Get the RGB values of the current pixel
            r,g,b = image.getpixel((x, y,))
            # print(r,g,b)
            if euclidean(target_color,(r,g,b,)) < tolerance:
                matching_pixels.append([x,y])
            
            
    region_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    for x, y in matching_pixels:
        region_image.putpixel((x, y), (*target_color, 255))
    if debug:
        region_image.show()
    return matching_pixels



def prominent_regions(ip):
    target_colors = get_prominent_colors(ip, number = 10)
    for color in target_colors:
        matched_pixels = identify_regions(ip, color[0], tolerance=50)

if __name__=='__main__':
    ip = 'examples/images/mantis_shrimp.jpeg'
    target_color = get_prominent_colors(ip)
    for color in target_color:
        print(cool_rgb_to_name(color[0]))
    
