# superwand

![SuperWand Studio](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/studio-preview.png)

Leverage magic wand to breath life to images, especially posterized and vector art images.

## Setup
```bash
pip install .
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
- `-k`: Number of regions to identify (default 4).
- `-tolerance`: Color matching tolerance (default 50).
- `-flood`: Apply morphological flood filling.
- `-gradient`: Gradient style (none, auto, vertical, horizontal, radial).
- `-intensity`: Gradient intensity (0.0 to 1.0, default 0.2).
- `--headless`: Run in headless mode without opening the studio.

### Enforce Gradients
```bash
gradient-enforce examples/images/charizard.png --style radial
```

#### Arguments
- `image_path`: Path to the input image.
- `--style`: Direction of gradients (auto, vertical, horizontal).
- `--completeness`: Impacted regions (auto, aggressive, filter).
- `--opacity`: Opacity handling.
- `--intensity`: Gradient dramaticism (0.0 to 1.0, default 0.2).
- `--output`: Path to the output image.


## Gradients
Included: `bottom-up`, `top-down`, `left-right`, `right-left`, `radial`

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_bottom-up_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_top-down_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_left-right_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_right-left_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_radial_charizard.png" width="150"></td>
  </tr>
</table>

## CSS Retheming
Identify color schemes in CSS and replace with a theme.

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/before.png" width="200"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/after_tropical.png" width="200"></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/menu.png" width="200"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/menu_tropical.png" width="200"></td>
  </tr>
</table>

## Color Themes
Themes included:

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/SpringTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/SummerTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/WinterTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/FallTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/ArcticTheme.jpg" width="100"></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/SafariTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/UrbanTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/NeonTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/TropicalTheme.jpg" width="100"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/src/superwand/assets/themes_jpgs/PaixãoTheme.jpg" width="100"></td>
  </tr>
</table>

### Example: Charizard

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Spring_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Summer_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Fall_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Winter_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Arctic_charizard.png" width="150"></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Safari_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Urban_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Neon_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Tropical_charizard.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Paixão_charizard.png" width="150"></td>
  </tr>
</table>

## Gallery

### Rio De Janeiro Skyline
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota.jpg" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Arctic.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Fall.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Neon.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Tropical.png" width="150"></td>
  </tr>
</table>

### Austin Ladybird Lake Plankton rendered in [ZIT](https://github.com/juleshenry/zooplankton-image-tool)
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19.jpg" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Spring.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Summer.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Winter.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Safari.png" width="150"></td>
  </tr>
</table>

### Me in Rio de Janeiro
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07.jpg" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Paixão.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Urban.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Arctic.png" width="150"></td>
    <td><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Fall.png" width="150"></td>
  </tr>
</table>
