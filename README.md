# superwand

![SuperWand Studio](https://github.com/juleshenry/superwand/blob/main/examples/studio-preview.png?raw=1)

Leverage magic wand to breath life to images, especially posterized and vector art images.

## Setup
```bash
uv sync
```

## SuperWand Studio

The SuperWand Studio provides an interactive web interface for real-time image retheming, CSS retheming, and gradient application.

### Running the Studio

Simply run the `superwand` command without applying a theme:
```bash
superwand
```

### Access the UI
Once the server is running, open your browser and navigate to `http://127.0.0.1:5001`.

## CLI Usage

### Apply a Theme
```bash
superwand examples/images/zebra.png -theme Urban
```

#### Arguments
- `image_path`: Path to the input image file (optional if starting studio).
- `-theme`: Theme to apply (Tropical, Urban, Winter, etc.).
- `-k`: Number of regions to identify (default: 4).
- `-tolerance`: Color matching tolerance (default: 50).
- `-flood`: Apply morphological flood filling (default: False).
- `-gradient`: Gradient style (none, auto, vertical, horizontal, radial, bottom-up, top-down, left-right, right-left) (default: none). When a theme is applied, the gradient transitions from the primary theme color of the region to the next color in the theme.
- `-polarity`: Gradient midpoint bias (0.0 to 1.0, default: 0.5). 0.5 is linear, lower values bias towards the start color, higher values bias towards the end color.

### Enforce Gradients
```bash
gradient-enforce examples/images/charizard.png --style radial --color1 "#FF0000" --color2 "#0000FF"
```

#### Arguments
- `image_path`: Path to the input image.
- `--style`: Direction of gradients (auto, vertical, horizontal, radial, bottom-up, top-down, left-right, right-left) (default: auto).
- `--completeness`: Impacted regions (auto, aggressive, filter) (default: auto).
- `--opacity`: Opacity handling (default: auto).
- `--polarity`: Gradient midpoint bias (0.0 to 1.0, default: 0.5).
- `--output`: Path to the output image (default: gradient_<style>_<filename>.png).
- `--color1`: Start color for the gradient (e.g., '255,0,0' or '#FF0000').
- `--color2`: End color for the gradient (e.g., '0,0,255' or '#0000FF').


> **Note on Colors**: By default, the start and end colors are automatically derived from each region's original color by adjusting its brightness. To explicitly define the gradient colors, use `--color1` and `--color2`. When provided, all prominent regions will be replaced with a gradient transitioning between these two colors.



## Gradients
Included: `bottom-up`, `top-down`, `left-right`, `right-left`, `radial`

| | | | | |
| :---: | :---: | :---: | :---: | :---: |
| ![bottom-up](https://github.com/juleshenry/superwand/blob/main/examples/charizards/gradient_bottom-up_charizard.png?raw=1) | ![top-down](https://github.com/juleshenry/superwand/blob/main/examples/charizards/gradient_top-down_charizard.png?raw=1) | ![left-right](https://github.com/juleshenry/superwand/blob/main/examples/charizards/gradient_left-right_charizard.png?raw=1) | ![right-left](https://github.com/juleshenry/superwand/blob/main/examples/charizards/gradient_right-left_charizard.png?raw=1) | ![radial](https://github.com/juleshenry/superwand/blob/main/examples/charizards/gradient_radial_charizard.png?raw=1) |

## CSS Retheming
Identify color schemes in CSS and replace with a theme.

| Before | After |
| :---: | :---: |
| ![before](https://github.com/juleshenry/superwand/blob/main/examples/css/before.png?raw=1) | ![after](https://github.com/juleshenry/superwand/blob/main/examples/css/after_tropical.png?raw=1) |
| ![menu](https://github.com/juleshenry/superwand/blob/main/examples/css/menu.png?raw=1) | ![menu_tropical](https://github.com/juleshenry/superwand/blob/main/examples/css/menu_tropical.png?raw=1) |

## Color Themes
Themes included:

| | | | | |
| :---: | :---: | :---: | :---: | :---: |
| ![Spring](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/SpringTheme.jpg?raw=1) | ![Summer](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/SummerTheme.jpg?raw=1) | ![Winter](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/WinterTheme.jpg?raw=1) | ![Fall](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/FallTheme.jpg?raw=1) | ![Arctic](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/ArcticTheme.jpg?raw=1) |
| ![Safari](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/SafariTheme.jpg?raw=1) | ![Urban](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/UrbanTheme.jpg?raw=1) | ![Neon](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/NeonTheme.jpg?raw=1) | ![Tropical](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/TropicalTheme.jpg?raw=1) | ![Paixão](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/Paix%C3%A3oTheme.jpg?raw=1) |
| ![Vaporwave](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/VaporwaveTheme.jpg?raw=1) | ![Cyberpunk](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/CyberpunkTheme.jpg?raw=1) | ![Retro80s](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/Retro80sTheme.jpg?raw=1) | ![Sunset](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/SunsetTheme.jpg?raw=1) | ![Midnight](https://github.com/juleshenry/superwand/blob/main/src/superwand/assets/themes_jpgs/MidnightTheme.jpg?raw=1) |

### Example: Charizard

| Spring | Summer | Fall | Winter | Arctic |
| :---: | :---: | :---: | :---: | :---: |
| ![Spring](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Spring_charizard.png?raw=1) | ![Summer](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Summer_charizard.png?raw=1) | ![Fall](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Fall_charizard.png?raw=1) | ![Winter](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Winter_charizard.png?raw=1) | ![Arctic](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Arctic_charizard.png?raw=1) |
| ![Safari](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Safari_charizard.png?raw=1) | ![Urban](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Urban_charizard.png?raw=1) | ![Neon](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Neon_charizard.png?raw=1) | ![Tropical](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Tropical_charizard.png?raw=1) | ![Paixão](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Paix%C3%A3o_charizard.png?raw=1) |
| ![Vaporwave](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Vaporwave_charizard.png?raw=1) | ![Cyberpunk](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Cyberpunk_charizard.png?raw=1) | ![Retro80s](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Retro80s_charizard.png?raw=1) | ![Sunset](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Sunset_charizard.png?raw=1) | ![Midnight](https://github.com/juleshenry/superwand/blob/main/examples/charizards/Midnight_charizard.png?raw=1) |

## Gallery

### Rio De Janeiro Skyline
| Original | Arctic | Fall | Neon | Tropical |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://github.com/juleshenry/superwand/blob/main/examples/gallery/erro_xota.jpg?raw=1) | ![Arctic](https://github.com/juleshenry/superwand/blob/main/examples/gallery/erro_xota_Arctic.png?raw=1) | ![Fall](https://github.com/juleshenry/superwand/blob/main/examples/gallery/erro_xota_Fall.png?raw=1) | ![Neon](https://github.com/juleshenry/superwand/blob/main/examples/gallery/erro_xota_Neon.png?raw=1) | ![Tropical](https://github.com/juleshenry/superwand/blob/main/examples/gallery/erro_xota_Tropical.png?raw=1) |

### Austin Ladybird Lake Plankton rendered in [ZIT](https://github.com/juleshenry/zooplankton-image-tool)
| Original | Spring | Summer | Winter | Safari |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://github.com/juleshenry/superwand/blob/main/examples/gallery/plankt_oct19.jpg?raw=1) | ![Spring](https://github.com/juleshenry/superwand/blob/main/examples/gallery/plankt_oct19_Spring.png?raw=1) | ![Summer](https://github.com/juleshenry/superwand/blob/main/examples/gallery/plankt_oct19_Summer.png?raw=1) | ![Winter](https://github.com/juleshenry/superwand/blob/main/examples/gallery/plankt_oct19_Winter.png?raw=1) | ![Safari](https://github.com/juleshenry/superwand/blob/main/examples/gallery/plankt_oct19_Safari.png?raw=1) |

### Me in Rio de Janeiro
| Original | Paixão | Urban | Arctic | Fall |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://github.com/juleshenry/superwand/blob/main/examples/gallery/rio07.jpg?raw=1) | ![Paixão](https://github.com/juleshenry/superwand/blob/main/examples/gallery/rio07_Paix%C3%A3o.png?raw=1) | ![Urban](https://github.com/juleshenry/superwand/blob/main/examples/gallery/rio07_Urban.png?raw=1) | ![Arctic](https://github.com/juleshenry/superwand/blob/main/examples/gallery/rio07_Arctic.png?raw=1) | ![Fall](https://github.com/juleshenry/superwand/blob/main/examples/gallery/rio07_Fall.png?raw=1) |
