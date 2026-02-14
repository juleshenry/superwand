import os
import sys
from PIL import Image, ImageDraw

# Add src to path to import superwand
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from superwand.core.themes import color_themes


def generate_palette_image(theme_name, colors, output_path):
    # Create an image with 8 blocks (2x4 or 1x8)
    # Let's go with 1x8 or 2x4. The existing ones seem to be small squares.
    block_size = 50
    rows = 2
    cols = 4
    width = cols * block_size
    height = rows * block_size

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    for i, color in enumerate(colors[:8]):
        r = i // cols
        c = i % cols
        left = c * block_size
        top = r * block_size
        right = left + block_size
        bottom = top + block_size
        draw.rectangle([left, top, right, bottom], fill=color)

    img.save(output_path, "JPEG", quality=95)
    print(f"Generated {output_path}")


def main():
    output_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "src", "superwand", "assets", "themes_jpgs"
        )
    )
    os.makedirs(output_dir, exist_ok=True)

    for theme_name, colors in color_themes.items():
        filename = f"{theme_name}Theme.jpg"
        output_path = os.path.join(output_dir, filename)
        generate_palette_image(theme_name, colors, output_path)


if __name__ == "__main__":
    main()
