from PIL import Image, ImageOps
import os

def create_gif(images, output_path, delay=100):
    # images: List of PIL image objects
    # output_path: Path to save the GIF
    # delay: Delay between frames in milliseconds (default: 100ms)

    # Convert the images to GIF frames
    frames = [img.convert('RGBA') for img in images]

    # Save the frames as an animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=delay,
        loop=0
    )

# if __name__ == "__main__":
#     # Replace 'image1.png', 'image2.png', etc., with your actual image file paths
#     image_files = ['image1.png', 'image2.png', 'image3.png']

#     # Load the images using PIL
#     images = [Image.open(file_path) for file_path in image_files]

#     # Specify the output file path
#     output_file = 'output.gif'

#     # Call the function to create the GIF with a 100ms delay
#     create_gif(images, output_file, delay=100)

#     from PIL import Image, ImageOps

import numpy as np
from PIL import Image

def get_distinct_colors(input_img):
    image = Image.open(input_img)
    img_array = np.array(image)
    sex = set()
    print(img_array[0][0])
    img_array[:, :3] = np.clip(255 - img_array[:, :3], 0, 255)
    print(img_array[0][0]);1/0
    # for x in img_array:
    #     all = tuple(tuple(y) for y in x)
    #     sex.add(all)
    # print(sorted(list(sex)))

def invert_image_numpy(input_filename, output_filename):
    # Load the image using PIL
    image = Image.open(input_filename)

    # Convert the image to a NumPy array
    img_array = np.array(image)

    # Invert the image using NumPy
    inverted_img_array = (255 - img_array) 

    # Create a new PIL image from the inverted NumPy array
    inverted_image = Image.fromarray(inverted_img_array)

    # Save the inverted image
    inverted_image.save(output_filename)

if __name__ == "__main__":
    iif = 'examples/pngs/pikachu_sprite.png' 
    # output_image_filename = 'output_image.png'
    # invert_image_numpy(input_image_filename, output_image_filename)

    get_distinct_colors(iif)