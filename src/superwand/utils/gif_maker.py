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

from PIL import Image, ImageOps
import os


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


import numpy as np
from PIL import Image


def inv(input_img):
    img_array = np.array(input_img)
    sex = set()
    img_array[:, :3] = 255 - img_array[:, :3]
    return Image.fromarray(img_array)


def invert_image_numpy(input_filename, output_filename):
    # Load the image using PIL
    image = Image.open(input_filename)
    # Invert the image using NumPy
    inverted_img = inv(image)
    # Save the inverted image
    inverted_img.save(output_filename)


if __name__ == "__main__":
    image_files = ["image1.png", "image2.png", "image3.png"]
    images = [Image.open(file_path) for file_path in image_files]
    output_file = "output.gif"
    create_gif(images, output_file, delay=100)
    iif = "examples/pngs/pickahu_sprite.png"
    invert_image_numpy(iif, "s.png")
