from superwand.np_colorgram import np_extract
from PIL import Image
import sys


def test_extract(img_path):
    print(f"Testing extraction on {img_path}")
    try:
        colors = np_extract(img_path, 4)
        print(f"Extracted {len(colors)} colors:")
        for c in colors:
            print(f"  {c}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_extract(sys.argv[1])
    else:
        # Try a default image
        test_extract("mantis_shrimp_Tropical.png")
