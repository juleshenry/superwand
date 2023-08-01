from PIL import Image

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

def invert_image(input_path, output_path):
    # Load the image using PIL
    image = Image.open(input_path)

    # Invert the image using ImageOps.invert()
    inverted_image = ImageOps.invert(image)

    # Save the inverted image
    inverted_image.save(output_path)

if __name__ == "__main__":
    # Replace 'input_image.png' with the path to your input image
    input_image_path = 'input_image.png'

    # Replace 'output_image.png' with the desired output path for the inverted image
    output_image_path = 'output_image.png'

    # Call the function to invert the image
    invert_image(input_image_path, output_image_path)
