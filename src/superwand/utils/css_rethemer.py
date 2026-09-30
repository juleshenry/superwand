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
import re
import sys
from sklearn.cluster import KMeans
import numpy as np
from ..core.themes import color_themes
from ..core.np_region_identifier import MATCH_MODES, match_palette

# #rgb, #rgba, #rrggbb, #rrggbbaa and rgb()/rgba() with comma or space syntax
COLOR_RE = re.compile(
    r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])"
    r"|\brgba?\(\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*(?:[,/]\s*([\d.]+%?)\s*)?\)",
    re.IGNORECASE,
)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    if len(hex_code) in (3, 4):
        hex_code = "".join(ch * 2 for ch in hex_code)
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def _read(css_file):
    if hasattr(css_file, "read"):
        content = css_file.read()
        if hasattr(css_file, "seek"):
            css_file.seek(0)
        return content.decode("utf-8") if isinstance(content, bytes) else content
    with open(css_file, encoding="utf-8") as f:
        return f.read()


def _in_declaration(css, start, end):
    """
    True if css[start:end] sits in a declaration value (`prop: <here>;`)
    rather than a selector like `#fade {` or `a:hover #abc,`.
    """
    before = max(css.rfind(c, 0, start) for c in "{};")
    if before == -1 or css[before] == "}" or ":" not in css[before + 1 : start]:
        return False
    after = [i for i in (css.find(c, end) for c in "{};") if i != -1]
    return not after or css[min(after)] != "{"


def find_colors(css_content):
    """Returns [(start, end, text, rgb, alpha_suffix)] for every color literal in a declaration."""
    # Blank out comments (keeping offsets) so banners and notes aren't recolored
    scan = COMMENT_RE.sub(lambda m: " " * len(m.group()), css_content)
    found = []
    for m in COLOR_RE.finditer(scan):
        if not _in_declaration(scan, m.start(), m.end()):
            continue
        text = m.group()
        if text.startswith("#"):
            digits = text[1:]
            rgb = hex_to_rgb(digits)
            alpha = ""
            if len(digits) in (4, 8):
                alpha = digits[-1] * 2 if len(digits) == 4 else digits[-2:]
        else:
            rgb = tuple(min(255, int(g)) for g in m.groups()[:3])
            alpha = m.group(4) or ""
        found.append((m.start(), m.end(), text, rgb, alpha))
    return found


def get_prominent_colors(css_file):
    """Returns [(rgb, original_text)] for every color literal in the stylesheet."""
    return [(rgb, text) for _, _, text, rgb, _ in find_colors(_read(css_file))]


def count_colors(colors):
    return Counter(colors)


def _format(original, rgb, alpha):
    if original.startswith("#"):
        return rgb_to_hex(rgb) + alpha.lower()
    if alpha:
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def css_retheme(css_file, theme_name=None, custom_theme=None, match="order"):
    """
    Clusters every color in the stylesheet and maps each cluster to a theme
    color. With match="order" the most-used cluster gets the first theme color;
    with match="luminance" dark clusters get dark theme colors. Alpha channels,
    formatting and everything that isn't a color are left untouched.
    """
    css_content = _read(css_file)
    found = find_colors(css_content)
    if not found:
        return css_content

    theme = list(custom_theme) if custom_theme else color_themes.get(
        theme_name, color_themes["Tropical"]
    )

    usage = Counter(rgb for *_, rgb, _ in found)
    unique = list(usage)
    n_clusters = min(len(theme), len(unique))
    kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto").fit(
        np.array(unique), sample_weight=[usage[c] for c in unique]
    )
    labels = kmeans.labels_

    # Order clusters by how often their colors are used, most-used first
    weight = Counter()
    for color, label in zip(unique, labels):
        weight[label] += usage[color]
    cluster_order = [label for label, _ in weight.most_common()]
    centers = [tuple(kmeans.cluster_centers_[label]) for label in cluster_order]
    assigned = dict(zip(cluster_order, match_palette(centers, theme, match)))
    replacement = {color: assigned[label] for color, label in zip(unique, labels)}

    out, last = [], 0
    for start, end, text, rgb, alpha in found:
        out.append(css_content[last:start])
        out.append(_format(text, replacement[rgb], alpha))
        last = end
    out.append(css_content[last:])
    return "".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Retheme every color in a CSS file with a SuperWand theme."
    )
    parser.add_argument("css_path", type=str, help="Path to the input CSS file.")
    parser.add_argument(
        "theme",
        type=str,
        choices=[ct for ct in color_themes],
        help="Theme to apply (Tropical, Urban, Winter, etc.).",
    )
    parser.add_argument(
        "--match",
        choices=MATCH_MODES,
        default="order",
        help="Pair clusters with theme colors by usage ('order') or brightness ('luminance').",
    )
    parser.add_argument(
        "-o", "--output", help="Output path (default: print to stdout)."
    )
    args = parser.parse_args()
    css = css_retheme(args.css_path, args.theme, match=args.match)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(css)
        print(f"Saved {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(css)


if __name__ == "__main__":
    main()
