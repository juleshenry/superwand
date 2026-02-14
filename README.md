# superwand
Leverage magic wand to breath life to images, especially posterized and vector art images.

## Setup
```bash
pip install .
```

## CLI Usage

### Apply a Theme
```bash
superwand examples/images/zebra.png -theme Urban
```

## SuperWand Studio

The SuperWand Studio provides an interactive web interface for real-time image retheming, CSS retheming, and gradient application.

### Running the Studio

1. **Setup Environment:**
   It is recommended to use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install . flask scikit-learn
   ```

2. **Start the Server:**
   Run the studio application from the root directory:
   ```bash
   export PYTHONPATH=$(pwd)/src
   python studio/app.py
   ```

3. **Access the UI:**
   Open your browser and navigate to `http://127.0.0.1:5001`.

### Features
- **Real-time Image Processing:** Upload an image and adjust the number of regions ($k$) and color matching tolerance.
- **Flood Logic:** Toggle "Aggressive" flooding to fill gaps in complex regions using morphological operations.
- **Custom Palettes:** Use dynamic color pickers or select from creative presets like **Cyberpunk**, **Vaporwave**, or **Retro80s**.
- **CSS Rethemer:** Upload a `.css` file and apply the active palette to it instantly.
- **Gradient Overlay:** Apply directional (Vertical, Horizontal) or Radial gradients to identified color regions.

### Enforce Gradients
```bash
gradient-enforce examples/images/charizard.png --style radial
```

## Gradients
Included: `bottom-up`, `top-down`, `left-right`, `right-left`, `radial`

<table>
  <tr>
    <td><img src="examples/charizards/gradient_bottom-up_charizard.png" width="150"></td>
    <td><img src="examples/charizards/gradient_top-down_charizard.png" width="150"></td>
    <td><img src="examples/charizards/gradient_left-right_charizard.png" width="150"></td>
    <td><img src="examples/charizards/gradient_right-left_charizard.png" width="150"></td>
    <td><img src="examples/charizards/gradient_radial_charizard.png" width="150"></td>
  </tr>
</table>

## CSS Retheming
Identify color schemes in CSS and replace with a theme.

<table>
  <tr>
    <td><img src="examples/css/before.png" width="200"></td>
    <td><img src="examples/css/after_tropical.png" width="200"></td>
  </tr>
  <tr>
    <td><img src="examples/css/menu.png" width="200"></td>
    <td><img src="examples/css/menu_tropical.png" width="200"></td>
  </tr>
</table>

## Color Themes
Themes included:

<table>
  <tr>
    <td><img src="themes_jpgs/SpringTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/SummerTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/WinterTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/FallTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/ArcticTheme.jpg" width="100"></td>
  </tr>
  <tr>
    <td><img src="themes_jpgs/SafariTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/UrbanTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/NeonTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/TropicalTheme.jpg" width="100"></td>
    <td><img src="themes_jpgs/PaixãoTheme.jpg" width="100"></td>
  </tr>
</table>

### Example: Charizard

<table>
  <tr>
    <td><img src="examples/charizards/Spring_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Summer_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Fall_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Winter_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Arctic_charizard.png" width="150"></td>
  </tr>
  <tr>
    <td><img src="examples/charizards/Safari_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Urban_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Neon_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Tropical_charizard.png" width="150"></td>
    <td><img src="examples/charizards/Paixão_charizard.png" width="150"></td>
  </tr>
</table>

## Gallery

### Erro Xota
<table>
  <tr>
    <td><img src="examples/gallery/erro_xota.jpg" width="150"></td>
    <td><img src="examples/gallery/erro_xota_Arctic.png" width="150"></td>
    <td><img src="examples/gallery/erro_xota_Fall.png" width="150"></td>
    <td><img src="examples/gallery/erro_xota_Neon.png" width="150"></td>
    <td><img src="examples/gallery/erro_xota_Tropical.png" width="150"></td>
  </tr>
</table>

### Plankt
<table>
  <tr>
    <td><img src="examples/gallery/plankt_oct19.jpg" width="150"></td>
    <td><img src="examples/gallery/plankt_oct19_Spring.png" width="150"></td>
    <td><img src="examples/gallery/plankt_oct19_Summer.png" width="150"></td>
    <td><img src="examples/gallery/plankt_oct19_Winter.png" width="150"></td>
    <td><img src="examples/gallery/plankt_oct19_Safari.png" width="150"></td>
  </tr>
</table>

### Rio 07
<table>
  <tr>
    <td><img src="examples/gallery/rio07.jpg" width="150"></td>
    <td><img src="examples/gallery/rio07_Paixão.png" width="150"></td>
    <td><img src="examples/gallery/rio07_Urban.png" width="150"></td>
    <td><img src="examples/gallery/rio07_Arctic.png" width="150"></td>
    <td><img src="examples/gallery/rio07_Fall.png" width="150"></td>
  </tr>
</table>
