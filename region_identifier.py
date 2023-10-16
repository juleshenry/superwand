from __color_themes__ import get_prominent_colors
from PIL import Image
import numpy as np
from scipy.spatial.distance import euclidean

def identify_regions(image_path, tolerance=20):
    # Convert target_color to RGB tuple if it's a string or hex
    target_color = get_prominent_colors(image_path)[0][0]
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
    region_image.show()

    return matching_pixels



if __name__=='__main__':
    # Example usage
    matched_pixels = identify_regions('examples/pngs/zebra.png', tolerance=50)
    # print(matched_pixels)