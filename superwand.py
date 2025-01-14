import argparse

from __color_themes__ import color_themes
from np_region_identifier import np_get_prominent_regions, np_inject_theme


class Img:
    pass


def flip(img: Img, direction="vertical") -> Img:
    if direction == "vertical":
        return img
    elif direction == "horizontal":
        return img
    else:
        return img


def gradient_enforce(
    img: Img, style="auto", completeness="auto", opacity="auto"
) -> Img:
    """
    Converts monocolor regionswith directional gradient

    style :
    ~ direction of gradients
            -> auto, best guess based on boosting
            -> vertical
            -> horizontal

    completeness :
    ~impacted regions
            -> aggressive, all colors
            -> auto, most impact
            -> filter, color or set of colors

    opacity :
    ~makes achieve minimum opacity value in region
            -> clamp {0, 1}
            -> failsafe rounds
    """
    if style == "auto":
        pass
    elif style == "vertical":
        pass
    elif style == "horizontal":
        pass
    else:
        style == "auto"

    if completeness == "auto":
        pass
    elif completeness == "aggressive":
        pass
    elif completeness == "filter":
        pass
    else:
        style == "auto"

    opacity = clamp(opacity, 0, 1)

    return img


class SuperWand:
    def __init__(self, color_themes):
        self.color_themes = color_themes

    def apply_theme_to_image(self, img_path, theme_name):
        list(
            map(
                lambda t: np_inject_theme(np_get_prominent_regions(img_path), t, img_path),
                self.color_themes if not theme_name else [theme_name],
            )
        )

    def apply_all_themes_to_image(self, img_path):
        for theme_name in self.color_themes:
            color_pix_dict = get_prominent_regions(img_path)
            inject_theme(color_pix_dict, theme_name, img_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process an image with a specified theme."
    )
    parser.add_argument("image_path", type=str, help="Path to the input image file.")
    parser.add_argument(
        "-theme",
        type=str,
        choices=[ct for ct in color_themes],
        
        help="Theme to apply (Tropical, Urban, Winter, etc.).",
    )
    args = parser.parse_args()
    sw = SuperWand(color_themes)
    sw.apply_theme_to_image(args.image_path, args.theme)
