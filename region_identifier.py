from __color_themes__ import get_prominent_colors
from PIL import Image
import numpy as np

def identify_regions(image_path, tolerance=50):
    """
    Identify regions in an image that match the target color.

    Args:
        image_path (str): Path to the image file.
        target_color (str or tuple): Color to be identified. Can be specified as a string ('red'), hex ('#FF5733'), or RGB tuple (255, 87, 51).
        tolerance (int): Tolerance for color matching. Default is 50.

    Returns:
        list: List of tuples representing the coordinates (x, y) of identified regions.
    """
    # Convert target_color to RGB tuple if it's a string or hex
    target_color = get_prominent_colors(image_path)[0]
    # Open the image
    image = Image.open(image_path)
    image_array = np.array(image)
    print(image_array[0])
    filled_array = np.full_like(image_array, target_color[0])
    # Find pixels matching the target color within tolerance
    # Calculate the color difference
    print(image_array.shape, filled_array.shape)
    color_diff = np.all(np.abs(image_array - filled_array) < tolerance, axis=-1)

    # Find pixels matching the target color within tolerance
    mask = color_diff 

    # Get coordinates of matching pixels
    matching_pixels = np.column_stack(np.where(mask))

    # Create a blank image with alpha channel
    region_image = Image.new('RGBA', image.size, (0, 0, 0, 0))

    # Paste matching pixels onto the blank image
    for x, y in matching_pixels:
        region_image.putpixel((x, y), (*target_color, 255))

    # Display the image with identified regions
    region_image.show()

    return matching_pixels



if __name__=='__main__':
    print('s')
    # Example usage
    matched_pixels = identify_regions('examples/pngs/zebra.png', tolerance=50)
    print(matched_pixels)