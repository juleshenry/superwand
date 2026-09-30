r"""
                                       ▂▃▃▃▄▄▄▄▃▂▃▃▂▁                                               
                                       ███████▇▃ ▅██▆                                               
                                       ▅██████▇▅▁███▃                                               
                                       ▄██████▇▃▁██▆▁                                               
                                       ▁▇██████▅▃██▅                                                
                                    ▁▃  ▇█████▆ ▁██▅ ▁▃▁                                            
                                    ███▆▇█████▆▁▁▇█▇▅██▇                                            
                                    ▇█████▇▇▇█▇▄▄▇▇▆███▅                                            
                                    ▁▃▇██████████████▆▂                                             
                                      ▁▁▅██▇▆▇▁▆▇▅█▆▁                                               
                                        ▁▆█▂ ▇▁▁ ▁▆▁                                                
                                         ▃█▇▆▆▇▅▅▇█▃                                                
                                      ▁▂▅▇▆▇▇▅▆▅▇▃▆▃▅▃▁                                             
                                  ▁▂▄▆▅▃▁▃▆▂▂▄▄▂▁▁▆ ▁▃▆█▆▅▃▁                                        
                                 ▂███▆▂  ▁▂▄▃▃▂▂▃▁▅  ▁▄█████▄                                       
                                ▁▇███▅▃▁          ▅  ▂▄▇█████▄▁                                     
                                ▄████▅▁  ▃▁       ▅   ▂███████▂                                     
                                ██████▄  ▄▁       ▅  ▂████████▇▁                                    
                               ▅███████▁ ▃▁  ▂    ▆ ▁▆█████████▄                                    
                              ▂████████▆▁▄▁  ▁   ▁▆▁▆███████████▁                                   
                              ▇█████████▅▄▂▁▁▂▁▂▂▄▆▂████████████▆                                   
                             ▄██████████▆▆█▅▆▆▄▃▃▅▇█████▇▅███████▃                                  
                            ▁██████████████▇▇▅▂ ▁▄██████▇▂████████▁                                 
                           ▁▄▅▄▅▇██▇██████▇▄▆▅▂  ▃███████▃▅█████▇▇▅▁                                
                           ▂▃    ▂█▆▇████████▆▃ ▁▅███████▄▁██▅▂▁  ▁▄▁                               
                           ▅▂▂▁▁▁▁▅▁▇██████████▇▆█████████▁▃▆    ▁▂▂▅                               
                           ▃▃▁▁▆▄▆▅▄██████████████████████▁ ▅▃▂▃▃▃▆▅▂                               
                          ▂▅▂▄▇▇▆▃ ▂██████████████████████▁ ▁▃▃▆▃▁▂▅▁                               
                          █▅ ▆▇▆   ▂██████████████████████▁    ▄▁▄▁▁▄                               
                        ▁▃██▂▅▅▃   ▂██████████████████████▁   ▁▅▄▂▇▁▅                               
                      ▂▅▇▅▃▄▃▂     ▂██████████████████████▁   ▁▃▄▅▇▃▄                               
                   ▁▃▆▆▃▁          ▁██████████████████████▁     ▁▅▅▂                                
                 ▂▄▇▅▁             ▁██████████████████████▁                                         
               ▁▂▆▃▁               ▁██████████▇███████████▁                                         
            ▁▁▁▁▁                  ▁▅█████████▂▄██████████▁                                         
          ▁▁▂▁▁                     ▃█████████▁▃▇█████████▁                                         
       ▂▁▂▂▁                        ▃█████████▁ ▄█████████                                          
       ▁▂▁                          ▁▅███████▆  ▃████████▃                                          
                                     ▃██████▇▁   ▇███████▂                                          
                                      ██████▇    ▁██████▇▂                                          
                                      ▂█████▃     ▇█████▁                                           
                                      ▂█████▂     ▄█████▁                                           
                                     ▂██████▄     ▄█████▆▁                                          
                                   ▁▄██████▆▃     ▃██████▇▂                                         
                                  ▁█████▆▂▁        ▁▂▅█████▅▁                                       
                                   ▂▂▂▂▁              ▁▄▅▇▇▇▂                                       
                                                                                                    

                                                                            ||` 
                                                                            ||  
       ('''' '||  ||` '||''|, .|''|, '||''| '\\    //`  '''|.  `||''|,  .|''||  
        `'')  ||  ||   ||  || ||..||  ||      \\/\//   .|''||   ||  ||  ||  ||  
       `...'  `|..'|.  ||..|' `|...  .||.      \/\/    `|..||. .||  ||. `|..||. 
                       ||                                                       
                      .||                                                       
                                  by Julian Henry 
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "arial.ttf"
)


def create_gif(images, output_path, delay=100):
    # images: List of PIL image objects
    # output_path: Path to save the GIF
    # delay: Delay between frames in milliseconds (default: 100ms)

    # Convert the images to GIF frames
    frames = [img.convert("RGBA") for img in images]

    # Save the frames as an animated GIF
    frames[0].save(
        output_path, save_all=True, append_images=frames[1:], duration=delay, loop=0
    )


def label_frame(img, text):
    """Draws `text` in a translucent bar along the bottom of the image."""
    img = img.convert("RGBA")
    size = max(14, img.height // 18)
    try:
        font = ImageFont.truetype(FONT_PATH, size)
    except OSError:
        font = ImageFont.load_default()
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bar = int(size * 1.6)
    draw.rectangle([0, img.height - bar, img.width, img.height], fill=(0, 0, 0, 150))
    draw.text(
        (size // 2, img.height - bar + (bar - size) // 2 - 2),
        text,
        font=font,
        fill=(255, 255, 255, 255),
    )
    return Image.alpha_composite(img, overlay)


def theme_cycle_gif(
    image,
    output_path,
    themes=None,
    k=4,
    delay=700,
    max_size=480,
    label=True,
    **retheme_kwargs,
):
    """
    Writes an animated GIF that cycles `image` through `themes` (default: all).
    Regions are computed once and reused for every frame.
    """
    from ..core.np_region_identifier import np_get_prominent_regions
    from ..core.superwand import retheme
    from ..core.themes import color_themes

    img = image if isinstance(image, Image.Image) else Image.open(image)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((max_size, max_size))
    regions = np_get_prominent_regions(img, number=k)

    frames = []
    for theme in themes or list(color_themes):
        frame = retheme(img, theme, k=k, regions=regions, **retheme_kwargs)
        frames.append(label_frame(frame, theme) if label else frame)
    create_gif(frames, output_path, delay=delay)
    return output_path


def inv(input_img):
    img_array = np.array(input_img)
    # Invert colour channels only; leave alpha untouched
    img_array[..., :3] = 255 - img_array[..., :3]
    return Image.fromarray(img_array)


def invert_image_numpy(input_filename, output_filename):
    # Load the image using PIL
    image = Image.open(input_filename)
    # Invert the image using NumPy
    inverted_img = inv(image)
    # Save the inverted image
    inverted_img.save(output_filename)


if __name__ == "__main__":
    theme_cycle_gif("examples/images/charizard.png", "charizard_themes.gif")
