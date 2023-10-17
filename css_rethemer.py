from colorthief import ColorThief
from collections import Counter


def get_prominent_colors(css_file):
    with open(css_file, 'r') as file:
        css_content = file.read()
    # Assuming the colors are in hexadecimal format
    colors = [c for c in css_content.split() if c.startswith("#")]
    return colors

def count_colors(colors):
   return Counter(colors)


def main():
    css_file = './site.css'  # Replace with the actual path
    colors = get_prominent_colors(css_file)
    print("Prominent colors in the CSS file:")
    color_counts = count_colors(colors)
    sorted_colors = dict(sorted(color_counts.items(), key=lambda item: item[1], reverse=True))
    print("Color Counts (Sorted):")
    for color, count in sorted_colors.items():
        print(f"{color}: {count} times")

if __name__ == "__main__":
    main()
