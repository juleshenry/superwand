# ✅ 1. Open image and identify major colors in text. Show color regions.
#  2. Prompt replacement selection
#  3. Get pixels of selected region
#  4. Form a convex hull polygon from the selected region
#  5. Insert a gradient, based on a color region, a new color twople and a type (vertical, radial, etc.)
from math import sqrt
from region_identifier import get_prominent_regions

def resolve_gradient_kw(gradient_direction):


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


from PIL import Image, ImageDraw, ImageFont

def create_image(rgb_tuples, grid_size, cell_size):
    width = grid_size[0] * cell_size
    height = grid_size[1] * cell_size
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    choice_font = ImageFont.truetype(font="./fonts/arial.ttf", size=36)

    for i, (r, g, b) in enumerate(rgb_tuples):
        x = (i % grid_size[0]) * cell_size
        y = (i // grid_size[0]) * cell_size

        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(r, g, b))
        label = f"({r}, {g}, {b})"
        draw.text((x + 5, y + 5), label, font=font, fill=("black" if (r+g+b > 100) else "white"))
        draw.text((x +  cell_size//3, y +  cell_size//3,), str(i+1), font=choice_font, fill = (abs(255-r),abs(255-g),abs(255-b),))

    return image

def append_images_vertically(image1_path, color_image, output_path=None):
    # Open the images
    image1 = color_image
    image2 = Image.open(image1_path)

    # Ensure both images have the same width
    width = max(image1.width, image2.width)

    # image1 = image1.resize((width, image1.height ))
    # image2 = image2.resize((width, image2.height ))

    # Create a new image with the combined height
    new_height = image1.height + image2.height
    result = Image.new('RGB', (width, new_height))
    
    # Paste the images one below the other
    result.paste(image1, (0, 0))
    result.paste(image2, (0, image1.height))
    result.show()
    if output_path:
        result.save(output_path)


def prompt_input(rgb_tuples):
    def handle_input():

    def prompt():
        for ij in enumerate(rgb_tuples):
            print(f'{ij[0]}_{ij}')
        i = input("Type the color # , comma-separated by the replacement rgb, also comma-separated")
        iss = i.split(',')
        if not len(iss)==5:
            raise ValueError("small.") #format : off
        handle_input(iss[0],iss[1:3])
if __name__=='__main__':
    ip = './examples/images/rocket_vector.jpeg'
    color_numbers = 16
    prs = get_prominent_regions(ip, number=color_numbers)
    grid_size = int(round(sqrt(color_numbers),0))
    rgb_tuples = prs.keys()
    grid_size = (grid_size, grid_size,)
    cell_size = 100
    output_image = create_image(rgb_tuples, grid_size, cell_size)
    append_images_vertically(ip, output_image)
    # output_image.show() 
    
