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

from collections import Counter
import argparse
from sklearn.cluster import KMeans
import numpy as np
from ..core.themes import color_themes


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    length = len(hex_code)
    return tuple(
        int(hex_code[i : i + length // 3], 16) for i in range(0, length, length // 3)
    )


import io

def get_prominent_colors(css_file):
    if hasattr(css_file, "read"):
        content = css_file.read()
        css_content = content.decode("utf-8") if isinstance(content, bytes) else content
        # Reset pointer if it's a file-like object for subsequent reads if necessary, 
        # though here we just return the colors.
        if hasattr(css_file, "seek"):
            css_file.seek(0)
    else:
        with open(css_file, "r") as file:
            css_content = file.read()
    
    # Assuming the colors are in hexadecimal format
    colors = []
    for text in css_content.split():
        if text.startswith("#"):
            try:
                kool = text.replace("#", "").replace(";", "").replace(":", "")
                colors.append((hex_to_rgb(kool), text))
            except:
                pass
    return colors


def count_colors(colors):
    return Counter(colors)


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def apply_clustering_theme(css_file, colors_text, kmp, theme):
    rep_dct = {
        ct[1]: rgb_to_hex(theme[kmp[ix] % len(theme)])
        for ix, ct in enumerate(colors_text)
    }
    modified_lines = []

    def replace_color(line):
        for style, theme_hex in rep_dct.items():
            if style in line:
                return line.replace(style, theme_hex)
        return None

    if hasattr(css_file, "read"):
        content = css_file.read()
        css_content = content.decode("utf-8") if isinstance(content, bytes) else content
        lines = css_content.splitlines()
    else:
        with open(css_file) as f:
            lines = f.readlines()

    for l in lines:
        rc = replace_color(l)
        modified_lines.append(l if not rc else rc.strip())

    return "\n".join(modified_lines)


def css_retheme(css_file, theme_name=None, custom_theme=None):
    colors_text = get_prominent_colors(css_file)
    if not colors_text:
        return ""
    colors = np.array([tup[0] for tup in colors_text])

    if custom_theme:
        theme = custom_theme
    else:
        theme = color_themes.get(theme_name, color_themes["Tropical"])

    kmeans = KMeans(
        n_clusters=min(len(theme), len(colors)), random_state=0, n_init="auto"
    ).fit(colors)
    kmeans_predictions = kmeans.predict(colors)
    return apply_clustering_theme(css_file, colors_text, kmeans_predictions, theme)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process an image with a specified theme."
    )
    parser.add_argument("image_path", type=str, help="Path to the input image file.")
    parser.add_argument(
        "theme",
        type=str,
        choices=[ct for ct in color_themes],
        help="Theme to apply (Tropical, Urban, Winter, etc.).",
    )
    args = parser.parse_args()
    css_retheme(args.image_path, args.theme)
