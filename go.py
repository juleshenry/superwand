from PIL import Image
import argparse


def superwand(image: Image):
    return


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Superwand")
    st = "store_true"
    parser.add_argument("--completeness", action=st, help="todo")  # fmt: skip
    parser.add_argument("--style", action=st, help="todo")  # fmt: skip
    parser.add_argument("--opacity", action=st, help="todo")  # fmt: skip
    # Parse the first argument
    args, positional_args = parser.parse_known_args()
    image = positional_args[0]
    # Access the option values
    if args.completeness:
        print("Text option is enabled")
    if args.style:
        print("Backsplash option is enabled")
    if args.opacity:
        print("Time stamp option is enabled")
    superwand(image)
