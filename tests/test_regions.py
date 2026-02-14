import numpy as np
from PIL import Image
from src.superwand.np_region_identifier import np_get_prominent_regions


def test():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:50, :50] = [255, 0, 0]
    img[50:, 50:] = [0, 255, 0]
    img[:50, 50:] = [0, 0, 255]
    img[50:, :50] = [255, 255, 255]

    img_path = "test_regions.png"
    Image.fromarray(img).save(img_path)

    regions = np_get_prominent_regions(img_path, number=4)
    print(f"Found {len(regions)} regions")
    for color, indices in regions.items():
        print(f"Color: {color}, Pixels: {len(indices)}")


if __name__ == "__main__":
    test()
