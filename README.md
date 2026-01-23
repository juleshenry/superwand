# superwand
[![PyPI version](https://badge.fury.io/py/superwand.svg)](https://badge.fury.io/py/superwand)
[![Coverage Status](https://coveralls.io/repos/github/juleshenry/superwand/badge.svg?branch=main)](https://coveralls.io/github/juleshenry/superwand?branch=main)
![Coverage](./coverage.svg)

`superwand` is a powerful posterization and color retheming tool that acts like a "magic wand" for images and CSS. It allows you to breathe new life into images (especially vector art and posterized graphics) by injecting gradients, enforcing color themes, or dynamically updating CSS stylesheets.

## Features
- **Gradient Injection**: Replace solid color regions with customizable gradients (radial, linear).
- **Automatic Gradient Enforcement**: Automatically identify prominent regions and apply gradients for a polished look.
- **CSS Retheming**: Dynamically update CSS color schemes based on predefined or custom themes.
- **Image Retheming**: Apply consistent color themes to your images with a single command.
- **Predefined Themes**: Includes 10+ professional color themes like Neon, Urban, Tropical, and more.

## Installation
```bash
pip install superwand
```

## Quick Start

### 1. Apply a Color Theme to an Image
Use the `superwand` command to instantly retheme an image:
```bash
superwand input.png -theme Urban
```

### 2. Inject Gradients Manually
Replace specific colors with gradients using `gradient_injector.py`:
```bash
python3 src/superwand/gradient_injector.py --input image.png --color "#FFFFFF" --gradient radial --start "#FF0000" --end "#0000FF"
```

### 3. Automatically Enforce Gradients
Let `superwand` decide where to put the magic:
```bash
python3 src/superwand/gradient_enforce.py input.png --style vertical --completeness aggressive
```

### 4. Retheme CSS Stylesheets
Update your website's look in seconds:
```bash
python3 src/superwand/css_rethemer.py site.css 'Tropical'
```

## Development
```bash
pip install -e .[dev]
```

## Testing
```bash
pytest
```

Color themes included:
<table>
  <tr>
    <td><img src="/themes_jpgs/SpringTheme.jpg" alt="Image 1"></td>
    <td><img src="/themes_jpgs/SummerTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/WinterTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/FallTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/ArcticTheme.jpg" alt="tropical">
  </tr>
  <tr>
    <td><img src="/themes_jpgs/SafariTheme.jpg" alt="Image 3"></td>
    <td><img src="/themes_jpgs/UrbanTheme.jpg" alt="Image 4"></td>
    <td><img src="/themes_jpgs/NeonTheme.jpg" alt="Image 4"></td>
    <td><img src="/themes_jpgs/TropicalTheme.jpg" alt="ADSF">
    <td><img src="/themes_jpgs/PaixãoTheme.jpg" alt="ADSF">
   </tr>
</table>

## Theme Descriptions
- **Spring**: Fresh greens, yellows, and light blues for a vibrant, natural feel.
- **Summer**: Warm oranges, reds, and blues evoking sunny beach vibes.
- **Fall**: Earthy reds, oranges, and browns like autumn leaves.
- **Winter**: Cool whites, blues, and silvers for icy, crisp aesthetics.
- **Arctic**: Pale whites and icy blues for polar-inspired designs.
- **Safari**: Browns, tans, and greens mimicking savanna landscapes.
- **Urban**: Grays, blacks, and metallics for city street styles.
- **Neon**: Electric pinks, cyans, and yellows for glowing, futuristic looks.
- **Tropical**: Bright pinks, blues, and purples for exotic, island themes.
- **Paixão**: Passionate reds, purples, and golds for intense, romantic palettes.

## Adding Custom Themes
To create your own theme, modify the `color_themes` dictionary in `__color_themes__.py`. Add a new key with a list of RGB color tuples (0-255).

Example:
```python
"MyCustomTheme": [(255, 100, 0), (0, 200, 100), (150, 50, 255)],
```

Then, use it: `superwand image.png -theme MyCustomTheme`. Contributions welcome!

Examples applied to Charizard:

<table>
  <tr>
    <td><img src="/examples/charizards/Spring_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Summer_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Fall_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Winter_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Arctic_charizard.png" alt="Image 3"></td>
  </tr>
  <tr>
    <td><img src="/examples/charizards/Safari_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Urban_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Neon_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Tropical_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Paixão_charizard.png" alt="Image 3"></td>
  </tr>
</table>

Some other fun examples:
<table>
  <tr>
    <td><img src="/examples/images/mantis_shrimp.jpeg" alt="Image 3"></td>
    <td><img src="/examples/images/Spring_mantis_shrimp.png" alt="Image 3"></td>
  </tr>
  <tr>
    <td><img src="/examples/images/obama.jpeg" alt="Image 3"></td>
    <td><img src="/examples/images/Fall_obama.png" alt="Image 3"></td>
  </tr>
</table>

# More Examples

## Rio
<table>
  <tr>
    <td><img src="/examples/more_examples/rio07.jpg" alt="Original"></td>
    <td><img src="/examples/more_examples/rio07_Neon.png" alt="Neon"></td>
    <td><img src="/examples/more_examples/rio07_Tropical.png" alt="Tropical"></td>
    <td><img src="/examples/more_examples/rio07_Safari.png" alt="Safari"></td>
  </tr>
</table>

## Plankton
<table>
  <tr>
    <td><img src="/examples/more_examples/plankt_oct19.jpg" alt="Original"></td>
    <td><img src="/examples/more_examples/plankt_oct19_Arctic.png" alt="Arctic"></td>
    <td><img src="/examples/more_examples/plankt_oct19_Paixão.png" alt="Paixão"></td>
    <td><img src="/examples/more_examples/plankt_oct19_Fall.png" alt="Fall"></td>
  </tr>
</table>

## Sad
<table>
  <tr>
    <td><img src="/examples/more_examples/sad.jpg" alt="Original"></td>
    <td><img src="/examples/more_examples/sad_Summer.png" alt="Summer"></td>
    <td><img src="/examples/more_examples/sad_Urban.png" alt="Urban"></td>
    <td><img src="/examples/more_examples/sad_Winter.png" alt="Winter"></td>
  </tr>
</table>

## IMG_7609
<table>
  <tr>
    <td><img src="/examples/more_examples/IMG_7609.jpg" alt="Original"></td>
    <td><img src="/examples/more_examples/IMG_7609_Spring.png" alt="Spring"></td>
    <td><img src="/examples/more_examples/IMG_7609_Fall.png" alt="Fall"></td>
  </tr>
</table>
