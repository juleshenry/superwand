# ✅ 1. Open image and identify major colors in text. Show color regions.
# ✅ 2. Prompt replacement selection
# ✅ 3. Get pixels of selected region
# ✅ 4. Form a convex hull polygon from the selected region
# ✅ 4. Form a convex hull polygon from the selected region
# ✅ 5. Insert a gradient, based on a color region, a new color twople and a type (vertical, radial, etc.)
from math import sqrt
from region_identifier import get_prominent_regions
from PIL import Image, ImageDraw, ImageFont
from gradients import linear_gradient, radial_gradient
from scipy.spatial import ConvexHull
import numpy as np
from prompt_input import prompt_input


def midpoint_hover(grad, pixel_arr):
    print("processing", grad)
    match grad:
        case "bottom-up":
            # y is min y
            # x is midpoint of low-x,high-x
            mid_x = (
                min([xy[0] for xy in pixel_arr]) + max([xy[0] for xy in pixel_arr])
            ) / 2
            min_y = min([xy[1] for xy in pixel_arr])
            max_y = max([xy[1] for xy in pixel_arr])
            return (mid_x, min_y), (mid_x, max_y)
        case "bottom-down":
            return (
                (0, 0),
                (0, -1),
            )
        case _:
            raise ValueError("fails")


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
        draw.text(
            (x + 5, y + 5),
            label,
            font=font,
            fill=("black" if (r + g + b > 100) else "white"),
        )
        draw.text(
            (
                x + cell_size // 3,
                y + cell_size // 3,
            ),
            str(i + 1),
            font=choice_font,
            fill=(
                abs(255 - r),
                abs(255 - g),
                abs(255 - b),
            ),
        )

    return image


def create_image_prompt(ip: str):
    color_numbers = 16
    prs = get_prominent_regions(ip, number=color_numbers)
    grid_size = int(round(sqrt(color_numbers), 0))
    grid_size = (
        grid_size,
        grid_size,
    )
    cell_size = 100
    prompt_image = create_image(prs.keys(), grid_size, cell_size)
    return prompt_image, prs


def prompted_single_change():
    # Choose base image
    ip = "./examples/images/charizard.png"
    # Create image prompt to allow choice, get prominent regions
    prompt_image, prs = create_image_prompt(ip)
    # Show prompt of color grid and replace.
    modified_image = prompt_input(
        Image.open(ip).convert("RGB"), prompt_image, prs, error=3
    )
    modified_image.save("modified_" + ip.split("/")[-1])


def gradient_single_change():
    # Choose base image
    ip = "./examples/images/charizard.png"
    # Create image prompt to allow choice, get prominent regions
    pixel_regions = get_prominent_regions(ip)
    color, polygon = list(pixel_regions.items())[1]
    print("Color:", color)
    polygon = [tuple(p) for p in polygon]
    img = Image.open(ip).convert("RGB")
    print(
        "Dimensions:",
        (img.width, img.height),
    )
    # from red to blue
    img = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))
    x = inject_gradient(img, polygon, (255,0,0,), (0,0,255,), "bottom-up")
    x.save("x.png")


def inject_gradient(img_class, pixel_arr, start_color, end_color, grad_dir):
    # Convert the list of points to a numpy array
    points = np.array(pixel_arr)
    # Compute the convex hull
    hull = ConvexHull(points)
    # The vertices of the convex hull will be in 'hull.vertices'
    convex_hull_points = list(map(tuple,points[hull.vertices].tolist()))
    # grad_vector = resolve_gradient_kw(grad_dir)
    p1, p2 = midpoint_hover(grad_dir, pixel_arr)
    print('calced mids',p1,p2)
    # p1, p2 = (img_class.width, 0), (0, img_class.height)
    # print((img_class, convex_hull_points, p1, p2, start_color, end_color),);1/0
    img = linear_gradient(img_class, convex_hull_points, p1, p2, start_color, end_color)
    return img


if __name__ == "__main__":
    gradient_single_change()
