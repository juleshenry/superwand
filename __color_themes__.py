from PIL import Image, ImageDraw, ImageFont
#from colorgram import extract
from np_colorgram import np_extract
from collections import Counter
import numpy as np
import os

def get_prominent_colors(image_path, number=4):
    # Extract #number of colors from the image, default is 4, the number for themes
    print('extractin')
    colors = extract(image_path, number)
    print('.done')
    # Count the occurrences of each color
    color_counter = Counter((color.rgb.r, color.rgb.g, color.rgb.b) for color in colors)
    # Get the four most common colors
    prominent_colors = color_counter.most_common(number)
    x = [pc[0] for pc in prominent_colors]
    return x

def np_get_prominent_colors(image_path, number=4):
    # Extract colors from the image
    print('extractin')
    colors = np_extract(image_path, number)
    print('.done')
    # Convert colors to a numpy array of RGB values
    rgb_values = np.array([(color.rgb.r, color.rgb.g, color.rgb.b) for color in colors])
    
    # Count unique RGB values and their occurrences
    unique_colors, counts = np.unique(rgb_values, axis=0, return_counts=True)
    print('np get prom')
    # Sort by counts in descending order and get the top 'number' colors
    top_indices = np.argsort(-counts)[:number]
    prominent_colors = unique_colors[top_indices]
    
    return prominent_colors.tolist()

# Define the color themes
color_themes = {
    "Spring": [(132, 255, 163), (255, 212, 77), (124, 252, 0), (255, 250, 205)],
    "Summer": [(255, 215, 0), (0, 191, 255), (46, 139, 87), (255, 140, 0)],
    "Winter": [(173, 216, 230), (240, 248, 255), (0, 0, 128), (135, 206, 250)],
    "Fall": [(255, 69, 0), (218, 165, 32), (128, 0, 0), (255, 99, 71)],
    "Safari": [(139, 69, 19), (154, 205, 50), (205, 133, 63), (139, 121, 94)],
    "Urban": [(149, 145, 140), (135, 135, 135), (99, 102, 94), (64, 66, 59)],
    "Neon": [(255, 105, 195), (70, 130, 195), (50, 205, 65), (255, 255, 15)],
    "Tropical": [(255, 165, 0), (255, 69, 0), (50, 205, 50), (30, 144, 255)],
    "Arctic": [(240, 255, 255), (173, 216, 230), (135, 206, 250), (70, 130, 180)],
    "Paixão": [(255, 101, 45), (255, 69, 109), (255, 85, 255), (255, 20, 147)],
}

# Define the size of each square
square_size = 16

# Define the size of the header
header_height = 30


def make_theme_splash():
    # Loop through the color themes
    for theme, colors in color_themes.items():
        # Calculate the width of the image
        img_width = square_size * len(colors)

        # Create a new blank image with header
        img = Image.new(
            "RGB", (img_width, square_size + header_height), color=(255, 255, 255)
        )

        # Draw the header with centered text
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text_width, text_height = font.getlength(theme), 12
        text_x = (img_width - text_width) // 2
        text_y = (header_height - text_height) // 2
        draw.text((text_x, text_y), theme, fill=(0, 0, 0), font=font)

        # Draw squares with the specified colors
        draw = ImageDraw.Draw(img)
        for i, color in enumerate(colors[0]):
            draw.rectangle(
                [
                    (i * square_size, header_height),
                    ((i + 1) * square_size, header_height + square_size),
                ],
                fill=color,
            )

        # Display the image
        img.save(f"themes_jpgs/{theme}Theme.jpg")



def np_make_theme_splash(color_themes, square_size=50, header_height=30, output_dir="themes_jpgs"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through the color themes
    for theme, colors in color_themes.items():
        # Calculate the width of the image
        img_width = square_size * len(colors)

        # Create a new blank image with header
        img = Image.new("RGB", (img_width, square_size + header_height), color=(255, 255, 255))

        # Draw the header with centered text
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text_width = font.getlength(theme)
        text_x = (img_width - text_width) // 2
        text_y = (header_height - 12) // 2  # Default font height is approximately 12
        draw.text((text_x, text_y), theme, fill=(0, 0, 0), font=font)

        # Draw squares with the specified colors
        for i, color in enumerate(colors):
            draw.rectangle(
                [
                    (i * square_size, header_height),
                    ((i + 1) * square_size, header_height + square_size),
                ],
                fill=color,
            )

        # Save the image to the output directory
        img.save(os.path.join(output_dir, f"{theme}Theme.jpg"))

def make_readme_includes():
    for c in color_themes:
        print(rf"![{c}](/themes_jpgs/{c}Theme.jpg)")


# make_theme_splash()
# make_readme_includes()
# # Can extract theme from any image
# get_prominent_colors('./examples/pngs/me.webp')
