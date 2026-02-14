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

import numpy as np
from PIL import Image
import os
from superwand.core.np_region_identifier import np_id_regiones


def test_id_regiones():
    # Create a simple 10x10 image with a red square in the middle
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[2:5, 2:5] = [255, 0, 0]  # Red square

    img_path = "test_img.png"
    Image.fromarray(img).save(img_path)

    target_color = [255, 0, 0]
    matches = np_id_regiones(img_path, target_color, tolerance=20)

    print(f"Target color: {target_color}")
    print(f"Found {len(matches)} matches")

    # Try with a color that is slightly off
    target_color_off = [250, 5, 5]
    matches_off = np_id_regiones(img_path, target_color_off, tolerance=20)
    print(f"Target color off: {target_color_off}")
    print(f"Found {len(matches_off)} matches (off)")

    # Try with a color that would cause negative overflow if uint8
    # e.g. pixel is [0,0,0], target is [10,10,10]
    # 0 - 10 = 246 in uint8. 246^2 is huge.
    target_color_dark = [10, 10, 10]
    matches_dark = np_id_regiones(img_path, target_color_dark, tolerance=20)
    print(f"Target color dark (on black pixels): {target_color_dark}")
    print(f"Found {len(matches_dark)} matches (dark)")

    os.remove(img_path)


if __name__ == "__main__":
    test_id_regiones()
