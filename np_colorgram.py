from __future__ import division, unicode_literals
import numpy as np
from collections import namedtuple
from PIL import Image

Rgb = namedtuple("Rgb", ("r", "g", "b"))
Hsl = namedtuple("Hsl", ("h", "s", "l"))

class Color:
    def __init__(self, r, g, b, proportion):
        self.rgb = Rgb(r, g, b)
        self.proportion = proportion

    def __repr__(self):
        return "<colorgram.py Color: {}, {}%>".format(
            str(self.rgb), str(self.proportion * 100)
        )

    # @property
    # def hsl(self):
    #     try:
    #         return self._hsl
    #     except AttributeError:
    #         self._hsl = Hsl(*self.hsl(*self.rgb))
    #         return self._hsl


def np_extract(image_path, number_of_colors):
    # Load the image and convert to RGB if necessary
    image = image_path if isinstance(image_path, Image.Image) else Image.open(image_path)
    if image.mode not in ("RGB", "RGBA", "RGBa"):
        image = image.convert("RGB")

    # Sample the image
    samples = np_sample(image)

    # Identify used color bins and their counts
    used = pick_used(samples)

    # Sort by count (descending order) and get the most common colors
    used.sort(key=lambda x: x[0], reverse=True)
    return get_colors(samples, used, number_of_colors)


def np_sample(image):
    # Constants
    top_two_bits = 0b11000000
    sides = 1 << 2  # 4 sides
    cubes = sides ** 7  # Color cube resolution

    # Create an array to hold sampled data
    samples = np.zeros((cubes, 4), dtype=np.int64)
    width, height = image.size
    pixels = np.array(image)  # Convert the image to a numpy array for faster processing

    # Flatten the array and separate RGB
    r, g, b = pixels[:, :, 0].flatten(), pixels[:, :, 1].flatten(), pixels[:, :, 2].flatten()

    # Compute HSL and luminance
    h, s, l = hsl_numpy(r, g, b)
    Y = (r * 0.2126 + g * 0.7152 + b * 0.0722).astype(np.int32)

    # Pack the top two bits of the luminance, hue, and luminosity
    packed = ((Y & top_two_bits) << 4) | ((h & top_two_bits) << 2) | ((l & top_two_bits) << 0)
    packed *= 4

    # Aggregate RGB and counts into the sample bins
    np.add.at(samples, (packed // 4), np.stack([r, g, b, np.ones_like(r)], axis=1))
    return samples


def pick_used(samples):
    # Get indices where the count (last column) is greater than 0
    non_zero_indices = np.nonzero(samples[:, 3])[0]
    counts = samples[non_zero_indices, 3]
    return list(zip(counts, non_zero_indices))


def get_colors(samples, used, number_of_colors):
    pixels = sum(count for count, _ in used[:number_of_colors])
    colors = []

    for count, index in used[:number_of_colors]:
        color = Color(
            samples[index, 0] // count,  # Average R
            samples[index, 1] // count,  # Average G
            samples[index, 2] // count,  # Average B
            count
        )
        colors.append(color)

    # Normalize proportions
    for color in colors:
        color.proportion /= pixels

    return colors


def hsl_numpy(r, g, b):
    # Compute max, min, and luminance
    max_val = np.maximum.reduce([r, g, b])
    min_val = np.minimum.reduce([r, g, b])
    l = (max_val + min_val) // 2

    # Compute the difference
    diff = max_val - min_val

    # Compute saturation
    s = np.zeros_like(l)
    denom1 = (510 - max_val - min_val)
    denom2 = (max_val + min_val)

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        s = np.where(l > 127, diff * 255 // denom1, diff * 255 // denom2)
        s = np.where(diff == 0, 0, s)

    # Compute hue
    h = np.zeros_like(r)
    mask = diff > 0
    h[mask & (max_val == r)] = (g[mask & (max_val == r)] - b[mask & (max_val == r)]) * 255 // diff[mask & (max_val == r)]
    h[mask & (max_val == g)] = (b[mask & (max_val == g)] - r[mask & (max_val == g)]) * 255 // diff[mask & (max_val == g)] + 510
    h[mask & (max_val == b)] = (r[mask & (max_val == b)] - g[mask & (max_val == b)]) * 255 // diff[mask & (max_val == b)] + 1020
    h = (h // 6) % 255  # Normalize hue to 0-255

    return h, s, l
