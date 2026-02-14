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

from superwand.core.np_colorgram import np_extract
from superwand.core.np_region_identifier import np_id_regiones
from PIL import Image
import sys
import numpy as np


def test_full_process(img_path):
    print(f"Testing process on {img_path}")
    try:
        img = Image.open(img_path).convert("RGB")
        img_array = np.array(img)

        colors = np_extract(img_path, 4)
        print(f"Extracted {len(colors)} colors")

        for i, c in enumerate(colors):
            rgb = [int(c.rgb.r), int(c.rgb.g), int(c.rgb.b)]
            matches = np_id_regiones(img_path, rgb, tolerance=50, img_array=img_array)
            print(
                f"  Color {i}: {rgb}, Proportion: {c.proportion * 100:.2f}%, Matches: {len(matches)} ({len(matches) / img_array.size * 300:.2f}% of pixels)"
            )

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_full_process(sys.argv[1])
    else:
        test_full_process("mantis_shrimp_Tropical.png")
