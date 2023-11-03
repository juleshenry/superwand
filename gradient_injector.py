from math import sqrt
from region_identifier import get_prominent_regions
from PIL import Image, ImageDraw, ImageFont
from gradients import paste_gradient
import numpy as np
from prompt_input import prompt_input
import math


def calc_gradient_poles(grad_kw, pixel_arr):
    print("processing", grad_kw)

    def calculate_distance(point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def farthest_point_from_center(_pixel_arr, center):
        farthest_point = None
        max_distance = float("-inf")
        for point in _pixel_arr:
            distance = calculate_distance(point, center)
            if distance > max_distance:
                max_distance = distance
                farthest_point = point
        return farthest_point

    match grad_kw:
        case "bottom-up":
            mid_x = (
                min([xy[0] for xy in pixel_arr]) + max([xy[0] for xy in pixel_arr])
            ) / 2
            min_y = min([xy[1] for xy in pixel_arr])
            max_y = max([xy[1] for xy in pixel_arr])
            return (mid_x, min_y), (mid_x, max_y)
        case "top-down":
            mid_x = (
                min([xy[0] for xy in pixel_arr]) + max([xy[0] for xy in pixel_arr])
            ) / 2
            min_y = min([xy[1] for xy in pixel_arr])
            max_y = max([xy[1] for xy in pixel_arr])
            return (mid_x, max_y), (mid_x, min_y)
        case "left-right":
            mid_y = (
                min([xy[1] for xy in pixel_arr]) + max([xy[1] for xy in pixel_arr])
            ) / 2
            min_x = min([xy[0] for xy in pixel_arr])
            max_x = max([xy[0] for xy in pixel_arr])
            return (min_x, mid_y), (max_x, mid_y)
        case "right-left":
            mid_y = (
                min([xy[1] for xy in pixel_arr]) + max([xy[1] for xy in pixel_arr])
            ) / 2
            min_x = min([xy[0] for xy in pixel_arr])
            max_x = max([xy[0] for xy in pixel_arr])
            return (max_x, mid_y), (min_x, mid_y)
        case "radial":
            sum_x = sum(point[0] for point in pixel_arr)
            sum_y = sum(point[1] for point in pixel_arr)
            center_x = sum_x / len(pixel_arr)
            center_y = sum_y / len(pixel_arr)
            center_xy = (center_x, center_y)
            farthest_point = farthest_point_from_center(pixel_arr, center_xy)
            return center_xy, farthest_point
        case _:
            raise ValueError(f"Unsupported gradient keyword {grad_kw}")


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


def gradient_single_change(start_color, end_color, grad_dir, color_to_replace=None):
    ip = "./examples/images/rocket_vector.jpeg"
    if not color_to_replace:
        pixel_regions = get_prominent_regions(ip, number=10)
        color, polygon = list(pixel_regions.items())[1]
    print("Replacing color:", color)
    polygon = [tuple(p) for p in polygon]
    img = Image.open(ip).convert("RGB")
    injected = inject_gradient(img, polygon, start_color, end_color, grad_dir)
    injected.save(f"gradient_{grad_dir}_{ip.split('/')[-1].split('.')[0]}.png")


def inject_gradient(img_class, pixel_arr, start_color, end_color, grad_dir):
    p1, p2 = calc_gradient_poles(grad_dir, pixel_arr)
    print("Calculated poles for gradient:", p1, p2)
    img = paste_gradient(img_class, pixel_arr, p1, p2, start_color, end_color, grad_dir)
    return img


if __name__ == "__main__":
    gradient_single_change((255,0,0,), (0,0,255,), "bottom-up")
    # gradient_single_change((255,0,0,), (0,0,255,), "top-down")
    # gradient_single_change((255,0,0,), (0,0,255,), "left-right")
    # gradient_single_change((255,0,0,), (0,0,255,), "right-left")
    # gradient_single_change(
    #     (
    #         255,
    #         0,
    #         0,
    #     ),
    #     (
    #         0,
    #         0,
    #         255,
    #     ),
    #     "radial",
    # )
