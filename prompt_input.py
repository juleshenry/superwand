from PIL import Image
from region_identifier import inject

def append_images_vertically(image1, image2, output_path=None):
    # Ensure both images have the same width
    width = max(image1.width, image2.width)

    # Create a new image with the combined height
    new_height = image1.height + image2.height
    result = Image.new("RGB", (width, new_height))

    # Paste the images one below the other
    result.paste(image2, (0, 0))
    result.paste(image1, (0, image2.height))
    result.show()
    if output_path:
        result.save(output_path)


def prompt_input(img, prompt_image, rgb_tuples, prs, error=None):
    delta = []

    def handle_input(img, pixel_arr, color):
        ii = inject(img, pixel_arr, color)
        return ii

    def prompt(_error=None):
        # Show color wheel and original image
        append_images_vertically(img, prompt_image)
        for ij in enumerate(rgb_tuples):
            print(f'{":".join(map(str,list(ij)))}')
        i = input(
            "Type the color # , comma-separated by the replacement rgb,"
            " also comma-separated\nElse, exit\n"
        )
        if _error:
            i = "3,0,255,0"
        iss = list(map(int, i.split(",")))
        if len(iss) != 4:
            raise ValueError("small.")  # format : off
        clean_choice_pixels = prs.get(list(rgb_tuples)[int(iss[0]) - 1])
        clean_color = tuple(iss[1:3])
        hi = handle_input(img, clean_choice_pixels, clean_color)
        return hi

    while len(delta) < 1:
        pr = prompt(error)
        delta.append(pr)
    delta[0].show()
