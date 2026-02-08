"""
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

from PIL import Image, ImageDraw, ImageFont
#from colorgram import extract
from .np_colorgram import np_extract
from collections import Counter
import numpy as np
import os


def np_get_prominent_colors(image_path, number=4):
    # Extract colors from the image
    print('extractin')
    colors = np_extract(image_path, number)
    # Convert colors to a numpy array of RGB values
    rgb_values = np.array([(color.rgb.r, color.rgb.g, color.rgb.b) for color in colors])
    
    # Count unique RGB values and their occurrences
    unique_colors, counts = np.unique(rgb_values, axis=0, return_counts=True)
    print('np get prom')
    # Sort by counts in descending order and get the top 'number' colors
    top_indices = np.argsort(-counts)[:number]
    prominent_colors = unique_colors[top_indices]
    print('>>>',prominent_colors)
    return prominent_colors.tolist()


# Define the color themes
CORES = {
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

CORES_DOIS = {
    "Spring": [
        (132, 255, 163), (255, 212, 77), (124, 252, 0), (255, 250, 205),
        (255, 182, 193), (173, 255, 47), (255, 105, 180), (240, 255, 240)
    ],
    "Summer": [
        (255, 215, 0), (0, 191, 255), (46, 139, 87), (255, 140, 0),
        (255, 99, 71), (255, 182, 193), (255, 20, 147), (32, 178, 170)
    ],
    "Winter": [
        (173, 216, 230), (240, 248, 255), (0, 0, 128), (135, 206, 250),
        (255, 250, 250), (70, 130, 180), (176, 224, 230), (0, 255, 255)
    ],
    "Fall": [
        (255, 69, 0), (218, 165, 32), (128, 0, 0), (255, 99, 71),
        (160, 82, 45), (139, 69, 19), (255, 140, 0), (205, 133, 63)
    ],
    "Safari": [
        (139, 69, 19), (154, 205, 50), (205, 133, 63), (139, 121, 94),
        (238, 232, 170), (240, 230, 140), (189, 183, 107), (160, 82, 45)
    ],
    "Urban": [
        (149, 145, 140), (135, 135, 135), (99, 102, 94), (64, 66, 59),
        (189, 183, 107), (128, 128, 128), (169, 169, 169), (211, 211, 211)
    ],
    "Neon": [
        (255, 105, 195), (70, 130, 195), (50, 205, 65), (255, 255, 15),
        (255, 20, 147), (138, 43, 226), (0, 255, 255), (255, 165, 0)
    ],
    "Tropical": [
        (255, 165, 0), (255, 69, 0), (50, 205, 50), (30, 144, 255),
        (255, 218, 185), (255, 99, 71), (0, 255, 255), (255, 105, 180)
    ],
    "Arctic": [
        (240, 255, 255), (173, 216, 230), (135, 206, 250), (70, 130, 180),
        (255, 250, 250), (224, 255, 255), (0, 191, 255), (176, 224, 230)
    ],
    "Paixão": [
        (255, 101, 45), (255, 69, 109), (255, 85, 255), (255, 20, 147),
        (255, 105, 180), (219, 112, 147), (238, 130, 238), (255, 182, 193)
    ]
}


class DOCbuddy:


    # make_theme_splash()
    # make_readme_includes()
    # # Can extract theme from any image
    # get_prominent_colors('./examples/pngs/me.webp')
    # Define the size of each square
    square_size = 16

    # Define the size of the header
    header_height = 30


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
        for c in CORES:
            print(rf"![{c}](/themes_jpgs/{c}Theme.jpg)")
