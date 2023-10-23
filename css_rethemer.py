from collections import Counter
import argparse
from sklearn.cluster import KMeans
import numpy as np
from __color_themes__ import color_themes


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    length = len(hex_code)
    return tuple(
        int(hex_code[i : i + length // 3], 16) for i in range(0, length, length // 3)
    )


def get_prominent_colors(css_file):
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


def apply_clustering_theme(css_file, colors_text, kmp, theme, theme_name):
    print(css_file)
    rep_dct = {ct[1]: rgb_to_hex(theme[kmp[ix]]) for ix, ct in enumerate(colors_text)}
    modified_lines = []
    x = f"{theme_name}_{css_file.split('/')[-1]}"

    def replace_color(line):
        for style, theme_hex in rep_dct.items():
            if style in line:
                return line.replace(style, theme_hex)
        return None

    with open(css_file) as f:
        for l in f.readlines():
            rc = replace_color(l)
            modified_lines.append(l if not rc else rc.strip())

    with open(x, "w") as file:
        file.write("\n".join(modified_lines))


def css_retheme(css_file, theme_name):
    colors_text = get_prominent_colors(css_file)
    colors = np.array([tup[0] for tup in colors_text])
    theme = color_themes[theme_name]
    kmeans = KMeans(n_clusters=len(theme), random_state=0, n_init="auto").fit(colors)
    kmeans_predictions = kmeans.predict(colors)
    apply_clustering_theme(css_file, colors_text, kmeans_predictions, theme, theme_name)


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
