import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


def linear_gradient(img_class, pixel_arr, start_pole, end_pole, start_color, end_color, grad_dr):
    draw = ImageDraw.Draw(img_class)
    spx,spy=start_pole
    epx,epy=end_pole
    w, h = img_class.size
    s_r, s_g, s_b = start_color
    e_r, e_g, e_b = end_color

    # left-right
    # for x,y in pixel_arr:
    #     r = int(s_r + (e_r - s_r) * (x / w))
    #     g = int(s_g + (e_g - s_g) * (x / w))
    #     b = int(s_b + (e_b - s_b) * (x / w))
    #     draw.point((x, y), fill=(r, g, b))

    # bottom-up
    for x,y in pixel_arr:
        r = int(s_r + (e_r - s_r) * ((y - spy) / (epy - spy)))
        g = int(s_g + (e_g - s_g) * ((y - spy) / (epy - spy)))
        b = int(s_b + (e_b - s_b) * ((y - spy) / (epy - spy)))
        draw.point((x, y), fill=(r, g, b))
    # img_class.paste(gradient_img)
    return img_class
    
    # # Paste gradient on blank canvas of sufficient size
    # temp = Image.new(
    #     "RGBA",
    #     (
    #         max(img_class.size[0], gradient.size[0]),
    #         max(img_class.size[1], gradient.size[1]),
    #     ),
    #     (0, 0, 0, 0),
    # )
    # temp.paste(gradient)
    # gradient = temp

    # # Rotate and translate gradient appropriately
    # x = np.sin(angle * np.pi / 180) * ht
    # y = np.cos(angle * np.pi / 180) * ht
    # gradient = gradient.rotate(-angle, center=(0, 0), translate=(p1[0] + x, p1[1] - y))

    # # Paste gradient on temporary image
    # ii.paste(gradient.crop((0, 0, ii.size[0], ii.size[1])), mask=ii)

    # # Paste temporary image on actual image
    # img_class.paste(ii, mask=ii)

    return img_class


# Draw polygon with radial gradient from point to the polygon border
# ranging from color 1 to color 2 on given image
def radial_gradient(i, poly, p, c1, c2):
    # Draw initial polygon, alpha channel only, on an empty canvas of image size
    ii = Image.new("RGBA", i.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ii)
    draw.polygon(poly, fill=(0, 0, 0, 255), outline=None)

    # Use polygon vertex with highest distance to given point as end of gradient
    p = np.array(p)
    max_dist = max([np.linalg.norm(np.array(v) - p) for v in poly])

    # Calculate color values (gradient) for the whole canvas
    x, y = np.meshgrid(np.arange(i.size[0]), np.arange(i.size[1]))
    c = np.linalg.norm(np.stack((x, y), axis=2) - p, axis=2) / max_dist
    c = np.tile(np.expand_dims(c, axis=2), [1, 1, 3])
    c = (c1 * (1 - c) + c2 * c).astype(np.uint8)
    c = Image.fromarray(c)

    # Paste gradient on temporary image
    ii.paste(c, mask=ii)

    # Paste temporary image on actual image
    i.paste(ii, mask=ii)

    return i




# # Draw first polygon with radial gradient
# polygon = [(100, 200), (320, 130), (460, 300), (700, 500), (350, 550), (200, 400)]
# point = (350, 350)
# color1 = (255, 0, 0)
# color2 = (0, 255, 0)
# image = radial_gradient(image, polygon, point, color1, color2)

# # Draw second polygon with linear gradient
# polygon = [(500, 50), (650, 250), (775, 150), (700, 25)]
# point1 = (700, 25)
# point2 = (650, 250)
# color1 = (255, 255, 0)
# color2 = (0, 0, 255)
# image = linear_gradient(image, polygon, point1, point2, color1, color2)

if __name__=='__main__':
    # Create blank canvas with zero alpha channel
    w, h = (800, 600)
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # Draw third polygon with linear gradient
    polygon = [(50, 550), (200, 575), (200, 500), (100, 300), (25, 450)]
    point1, point2 = (100, 300), (200, 575)
    color1, color2 = (255, 255, 255), (255, 128, 0)
    image = linear_gradient(image, polygon, point1, point2, color1, color2)
    # Save image
    image.save("simple_linear.png")
