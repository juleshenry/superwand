# superwand

[![PyPI](https://img.shields.io/pypi/v/superwand)](https://pypi.org/project/superwand/)
[![Python](https://img.shields.io/pypi/pyversions/superwand)](https://pypi.org/project/superwand/)
[![CI](https://github.com/juleshenry/superwand/actions/workflows/ci.yml/badge.svg)](https://github.com/juleshenry/superwand/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/pypi/l/superwand)](LICENSE)

Retheme images, SVG and CSS with color palettes and gradients. superwand finds the main color
regions of a picture and repaints each one from a theme. It suits posterized art, sprites and
vector illustrations, and works on photos too.

![Every theme, one Charizard](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/charizard_themes.gif)

## Install

```bash
pip install superwand                # library and CLI
pip install "superwand[studio]"      # plus the SuperWand Studio web app
```

Or run it without installing: `uvx superwand art.png -t Neon`. Needs Python 3.10 or newer.

## Quick start

```bash
superwand art.png -t Vaporwave                      # writes art_Vaporwave.png
superwand art.png                                   # one file per theme
superwand photo.jpg -t Fall --preserve-shading --smooth
superwand logo.svg site.css -t "#ff0080,#00ffff,#1a0033"
superwand rocket.png --palette-from shrimp.jpg -k 6 # steal another image's palette
superwand sprites/ -t Arctic -j 4 -o out/           # a whole folder, in parallel
superwand                                           # open SuperWand Studio
```

```python
from superwand import retheme

retheme("art.png", "Vaporwave", k=6).save("art_vaporwave.png")
```

## Features

- **Region-based retheming.** k-means splits an image into its `k` most prominent color regions,
  measured in the perceptual OKLab color space, and paints each region with a theme color.
- **Transparency is preserved.** Transparent backgrounds stay transparent, so sprites and icons
  keep working.
- **Preserve shading.** `--preserve-shading` keeps each pixel's light and shadow, so photos look
  recolored instead of posterized.
- **Smooth edges.** `--smooth` blends anti-aliased edge pixels between neighboring regions.
- **Gradients.** Linear and radial gradients per region with a movable midpoint (`--polarity`),
  blended in OKLab so a blue-to-yellow gradient doesn't turn gray in the middle.
- **SVG and CSS.** In SVG, recolors `fill`, `stroke`, `stop-color`, `style` attributes and
  `<style>` blocks. In CSS, recolors every hex, `rgb()`, `hsl()`, `oklch()`, `oklab()` and named
  color, keeping formatting and alpha, with optional WCAG contrast repair.
- **Any palette.** 18 built-in themes, a color list on the command line, palette files (JSON,
  TOML, GIMP `.gpl`, Adobe `.ase`, `.hex`), your own themes folder, or the colors of another image.
- **Region control.** Keep a region's original pixels (`--lock`) or pin it to a color (`--map`).
- **Palette export.** Save an image's dominant colors as hex, JSON, CSS variables, `.gpl` or `.ase`.
- **SuperWand Studio.** A local web app for retheming with live previews. It works offline.

## Command line

```
superwand [INPUT ...] [options]
```

Inputs can be images, `.svg` or `.css` files, folders, or glob patterns. Without inputs,
`superwand` starts SuperWand Studio. Each result is saved as `<name>_<theme>.<ext>` in the
output folder.

| Option | What it does |
| --- | --- |
| `-t, --theme THEME` | Theme name (case-insensitive), palette file, or colors like `"#ff0080,#00ffff"`. Repeat for several. Default: every theme. |
| `--palette-from IMAGE` | Use the `k` dominant colors of another image as the theme. |
| `-k K` | Number of color regions (default 4). |
| `--match order\|luminance` | Pair regions with colors by size (`order`, the default for themes) or by brightness (`luminance`, the default for `--palette-from`). |
| `--preserve-shading` | Keep each pixel's lightness relative to its region. Best for photos. |
| `--smooth` | Blend colors across region edges. |
| `--gradient STYLE` | `top-down`, `bottom-up`, `left-right`, `right-left` or `radial` (aliases: `auto`, `vertical`, `horizontal`). |
| `--polarity P` | Where along the gradient the 50/50 blend lands, 0 to 1 (default 0.5). |
| `--flood` | Close holes in regions and grow them slightly. |
| `--lock N` | Keep region N's original pixels. Regions are numbered from 1, largest first. |
| `--map N=COLOR` | Paint region N with COLOR, e.g. `--map 2=#ff0080` or `--map 3=navy`. |
| `--space oklab\|rgb` | Color space for finding regions (default `oklab`). |
| `--min-contrast RATIO` | CSS: fix text colors below this WCAG contrast with their background (e.g. `4.5`). |
| `--palette [FILE]` | Print the image's numbered regions and colors, or save them to FILE (`.hex`, `.json`, `.css`, `.gpl`, `.ase`). |
| `--format FMT` | Palette format for `--palette`: `text`, `hex`, `json`, `css`, `gpl` or `ase`. |
| `--gif` | Write an animated GIF that cycles through the themes. |
| `-o, --output-dir DIR` | Where to write results (default: current folder). |
| `-j, --jobs N` | Process inputs in parallel. |
| `--list-themes` | List built-in and user themes. |
| `--host`, `--port`, `--debug` | Studio server options (default `127.0.0.1:5001`). |

Run `superwand art.png --palette` to see the region numbers that `--lock` and `--map` use:

```
$ superwand charizard.png --palette
  1  #fea654  rgb(254, 166, 84)    27.9%
  2  #d45332  rgb(212, 83, 50)     26.2%
  3  #1a1010  rgb(26, 16, 16)      24.4%
  4  #fffffe  rgb(255, 255, 254)   21.5%
```

The pre-0.4 spellings (`-theme`, `-gradient`, `-palette-from`, ...) still work.

### gradient-enforce

Turns each flat color region into a gradient, either from a lighter to a darker shade of its own
color or between two colors you choose.

```bash
gradient-enforce charizard.png --style radial --color1 "#ff0000" --color2 "#0000ff"
```

Options: `--style`, `--polarity`, `--color1`/`--color2` (given together), `-k`, `--output`.

### css-retheme

Rethemes a single CSS or SVG file and prints the result, or writes it with `-o`.

```bash
css-retheme site.css Tropical -o site_tropical.css
css-retheme site.css Neon --min-contrast 4.5 -o site_neon.css   # keep text readable
css-retheme site.css --check                                     # list low-contrast pairs
```

## Python API

```python
from superwand import (
    find_regions,
    retheme,
    transfer_palette,
    extract_palette,
    gradient_enforce,
    svg_retheme,
    css_retheme,
    theme_cycle_gif,
    save_palette,
)

img = retheme("charizard.png", "Vaporwave", k=6, gradient="radial")  # an RGBA PIL Image
img = retheme("photo.jpg", "Fall", shading=True, smooth=True)
img = retheme("art.png", "#ff0080, #00ffff, navy")  # any palette form
img = retheme("art.png", "Neon", overrides={0: None, 2: "#123456"})  # lock / pin regions
img = transfer_palette("rocket.jpeg", "mantis_shrimp.jpeg", k=6)

regions = find_regions("charizard.png", k=4)  # compute once, reuse for many themes
frames = [retheme("charizard.png", t, regions=regions) for t in ("Neon", "Arctic")]
regions.colors, regions.counts  # region colors and sizes, largest first

colors = extract_palette("mantis_shrimp.jpeg", 6)  # [(r, g, b), ...]
save_palette(colors, "shrimp.ase")  # or .gpl .json .css .hex
svg = svg_retheme("logo.svg", "Forest")
css = css_retheme("site.css", "Tropical", min_contrast=4.5)
theme_cycle_gif("charizard.png", "charizard_themes.gif")
```

`retheme()` accepts a path or a PIL image and always returns RGBA. Region indexes in
`overrides` start at 0 for the largest region.

## Custom themes

A theme can be any of these:

- a built-in name: `Neon`, `neon` and `paixao` all work;
- a color list: `"#ff0080,#00ffff,#1a0033"` or `"hotpink navy rgb(0 200 120)"`;
- a palette file: `.json` (`["#ff0080", ...]` or `{"name": ..., "colors": [...]}`), `.toml`
  (`name = ...` and `colors = [...]`), GIMP `.gpl`, Adobe `.ase`, `.hex`/`.txt` (one color per
  line, Lospec style), or CSS custom properties in a `.css` file;
- a file in your themes folder, used by name. The folder is `~/.config/superwand/themes`
  (`%APPDATA%\superwand\themes` on Windows); set `SUPERWAND_THEMES_DIR` to use another one.
  User themes show up in `--list-themes` and in the Studio.

### Built-in themes

|  |  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Spring** <br> ![Spring](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/SpringTheme.jpg) | **Summer** <br> ![Summer](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/SummerTheme.jpg) | **Winter** <br> ![Winter](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/WinterTheme.jpg) | **Fall** <br> ![Fall](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/FallTheme.jpg) | **Arctic** <br> ![Arctic](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/ArcticTheme.jpg) | **Safari** <br> ![Safari](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/SafariTheme.jpg) |
| **Urban** <br> ![Urban](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/UrbanTheme.jpg) | **Neon** <br> ![Neon](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/NeonTheme.jpg) | **Tropical** <br> ![Tropical](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/TropicalTheme.jpg) | **Paixão** <br> ![Paixão](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/Paix%C3%A3oTheme.jpg) | **Vaporwave** <br> ![Vaporwave](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/VaporwaveTheme.jpg) | **Cyberpunk** <br> ![Cyberpunk](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/CyberpunkTheme.jpg) |
| **Retro80s** <br> ![Retro80s](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/Retro80sTheme.jpg) | **Sunset** <br> ![Sunset](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/SunsetTheme.jpg) | **Midnight** <br> ![Midnight](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/MidnightTheme.jpg) | **Forest** <br> ![Forest](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/ForestTheme.jpg) | **Oceanic** <br> ![Oceanic](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/OceanicTheme.jpg) | **Volcano** <br> ![Volcano](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/themes/VolcanoTheme.jpg) |

## SuperWand Studio

![SuperWand Studio](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/studio-preview.png)

SuperWand Studio is a local web app for interactive retheming. Upload an image, drag the `k`
slider, pick colors per region, add gradients, toggle smooth edges and preserve shading, compare
before and after, and download the result. It also rethemes CSS and SVG files. Install it with
`pip install "superwand[studio]"`, run `superwand`, then open <http://127.0.0.1:5001>.

## Demos

All images below are generated by `uv run python scripts/generate_demos.py`.

### Transparency, smooth edges and locked regions

![transparency](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/transparency.webp)

### Preserve shading on photos

Plain retheming posterizes a photo. `--smooth` softens region borders, and `--preserve-shading`
keeps the original light and shadow.

![shading](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/shading.webp)

### Choosing `k`

More regions means finer-grained recoloring.

![k sweep](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/k_sweep.webp)

### Palette transfer

`--palette-from` extracts the dominant colors of a reference image and applies them with
luminance matching, so dark stays dark and light stays light.

![palette transfer](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/palette_transfer.webp)

### Matching by order vs. luminance

With `match=order` colors are assigned by region size, so a bright sunset sky can turn dark.
With `match=luminance` the sky gets the theme's lightest color and the silhouetted mountains its
darkest.

![match modes](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/match_modes.webp)

### Gradient polarity

![polarity sweep](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/demos/polarity_sweep.webp)

### Gradients

|  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: |
| **bottom-up** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_bottom-up_charizard.png" width="160" alt="bottom-up"> | **top-down** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_top-down_charizard.png" width="160" alt="top-down"> | **left-right** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_left-right_charizard.png" width="160" alt="left-right"> | **right-left** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_right-left_charizard.png" width="160" alt="right-left"> | **radial** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/gradient_radial_charizard.png" width="160" alt="radial"> |

### SVG

```bash
superwand sunset.svg -t Vaporwave -t Forest -t Arctic -t Volcano --match luminance
```

|  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: |
| **Original** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/svg/sunset.svg" width="200" alt="Original"> | **Vaporwave** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/svg/sunset_Vaporwave.svg" width="200" alt="Vaporwave"> | **Forest** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/svg/sunset_Forest.svg" width="200" alt="Forest"> | **Arctic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/svg/sunset_Arctic.svg" width="200" alt="Arctic"> | **Volcano** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/svg/sunset_Volcano.svg" width="200" alt="Volcano"> |

### CSS

Every color in a declaration is clustered, and each cluster is mapped to a theme color.
Selectors, comments, formatting and alpha channels are left alone.

```bash
css-retheme examples/css/site.css Tropical -o site_tropical.css
```

| Before | After |
| :---: | :---: |
| ![before](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/before.png) | ![after](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/after_tropical.png) |
| ![menu](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/menu.png) | ![menu_tropical](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/css/menu_tropical.png) |

### Charizard in every theme

|  |  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Spring** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Spring_charizard.png" width="160" alt="Spring"> | **Summer** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Summer_charizard.png" width="160" alt="Summer"> | **Winter** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Winter_charizard.png" width="160" alt="Winter"> | **Fall** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Fall_charizard.png" width="160" alt="Fall"> | **Arctic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Arctic_charizard.png" width="160" alt="Arctic"> | **Safari** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Safari_charizard.png" width="160" alt="Safari"> |
| **Urban** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Urban_charizard.png" width="160" alt="Urban"> | **Neon** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Neon_charizard.png" width="160" alt="Neon"> | **Tropical** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Tropical_charizard.png" width="160" alt="Tropical"> | **Paixão** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Paix%C3%A3o_charizard.png" width="160" alt="Paixão"> | **Vaporwave** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Vaporwave_charizard.png" width="160" alt="Vaporwave"> | **Cyberpunk** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Cyberpunk_charizard.png" width="160" alt="Cyberpunk"> |
| **Retro80s** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Retro80s_charizard.png" width="160" alt="Retro80s"> | **Sunset** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Sunset_charizard.png" width="160" alt="Sunset"> | **Midnight** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Midnight_charizard.png" width="160" alt="Midnight"> | **Forest** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Forest_charizard.png" width="160" alt="Forest"> | **Oceanic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Oceanic_charizard.png" width="160" alt="Oceanic"> | **Volcano** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/charizards/Volcano_charizard.png" width="160" alt="Volcano"> |

## Gallery

### Rio De Janeiro Skyline
| Original | Arctic | Fall | Neon | Tropical |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota.jpg) | ![Arctic](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Arctic.webp) | ![Fall](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Fall.webp) | ![Neon](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Neon.webp) | ![Tropical](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/erro_xota_Tropical.webp) |

### Austin Ladybird Lake Plankton rendered in [ZIT](https://github.com/juleshenry/zooplankton-image-tool)
| Original | Spring | Summer | Winter | Safari |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19.jpg) | ![Spring](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Spring.webp) | ![Summer](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Summer.webp) | ![Winter](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Winter.webp) | ![Safari](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/plankt_oct19_Safari.webp) |

### Me in Rio de Janeiro
| Original | Paixão | Urban | Arctic | Fall |
| :---: | :---: | :---: | :---: | :---: |
| ![Original](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07.jpg) | ![Paixão](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Paix%C3%A3o.webp) | ![Urban](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Urban.webp) | ![Arctic](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Arctic.webp) | ![Fall](https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/rio07_Fall.webp) |

### Night Portrait, December 2017

<p align="center"><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait.jpg" width="180" alt="Original"><br><b>Original</b></p>

|  |  |  |  |
| :---: | :---: | :---: | :---: |
| **Spring** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Spring.webp" width="180" alt="Spring"> | **Summer** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Summer.webp" width="180" alt="Summer"> | **Winter** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Winter.webp" width="180" alt="Winter"> | **Fall** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Fall.webp" width="180" alt="Fall"> |
| **Safari** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Safari.webp" width="180" alt="Safari"> | **Urban** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Urban.webp" width="180" alt="Urban"> | **Neon** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Neon.webp" width="180" alt="Neon"> | **Tropical** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Tropical.webp" width="180" alt="Tropical"> |
| **Arctic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Arctic.webp" width="180" alt="Arctic"> | **Paixão** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Paix%C3%A3o.webp" width="180" alt="Paixão"> | **Cyberpunk** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Cyberpunk.webp" width="180" alt="Cyberpunk"> | **Sunset** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Sunset.webp" width="180" alt="Sunset"> |
| **Oceanic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Oceanic.webp" width="180" alt="Oceanic"> | **Vaporwave** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Vaporwave.webp" width="180" alt="Vaporwave"> | **Retro80s** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Retro80s.webp" width="180" alt="Retro80s"> | **Volcano** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/night_portrait_Volcano.webp" width="180" alt="Volcano"> |

### Dad at the Beach

<p align="center"><img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses.jpg" width="240" alt="Original"><br><b>Original</b></p>

|  |  |  |  |
| :---: | :---: | :---: | :---: |
| **Spring** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Spring.webp" width="200" alt="Spring"> | **Summer** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Summer.webp" width="200" alt="Summer"> | **Winter** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Winter.webp" width="200" alt="Winter"> | **Fall** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Fall.webp" width="200" alt="Fall"> |
| **Safari** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Safari.webp" width="200" alt="Safari"> | **Urban** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Urban.webp" width="200" alt="Urban"> | **Neon** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Neon.webp" width="200" alt="Neon"> | **Tropical** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Tropical.webp" width="200" alt="Tropical"> |
| **Arctic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Arctic.webp" width="200" alt="Arctic"> | **Paixão** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Paix%C3%A3o.webp" width="200" alt="Paixão"> | **Cyberpunk** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Cyberpunk.webp" width="200" alt="Cyberpunk"> | **Sunset** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Sunset.webp" width="200" alt="Sunset"> |
| **Oceanic** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Oceanic.webp" width="200" alt="Oceanic"> | **Vaporwave** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Vaporwave.webp" width="200" alt="Vaporwave"> | **Retro80s** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Retro80s.webp" width="200" alt="Retro80s"> | **Volcano** <br> <img src="https://raw.githubusercontent.com/juleshenry/superwand/main/examples/gallery/dad_sunglasses_Volcano.webp" width="200" alt="Volcano"> |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, checks and the release process, and
[CHANGELOG.md](CHANGELOG.md) for what changed in each version.

## License

[MIT](LICENSE) © Julian Henry
