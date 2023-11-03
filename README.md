# superwand
Leverage magic wand to breath life to images, especially posterized and vector art images.


# Example: Arbitrary color replacement on posterized images
## Example: 
```python3 gradient_injector.py```


Gradients included: bottom-up, top-down, left-right, right-left, bottom-down, radial
<table>
  <tr>
    <td><img src="/examples/charizards/gradient_bottom-up_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/gradient_top-down_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/gradient_left-right_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/gradient_right-left_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/gradient_radial_charizard.png" alt="Image 3"></td>
  </tr>
</table>
<table>
  <tr>
    <td><img src="/examples/images/rocket_vector.jpeg" alt="Image 3"></td>
    <td><img src="/examples/images/gradient_bottom-up_rocket_vector.png" alt="Image 3"></td>
  </tr>
</table>
# Given a CSS style sheet, dynamically identify color scheme and replace with a theme
## Example:
```python3 superwand.py examples/css/site.css 'Tropical'```

<table>
  <tr>
    <td><img src="/examples/css/before.png" alt="Image 3"></td>
    <td><img src="/examples/css/after_tropical.png" alt="Image 3"></td>
  </tr>
    <tr>
    <td><img src="/examples/css/menu.png" alt="Image 3"></td>
    <td><img src="/examples/css/menu_tropical.png" alt="Image 3"></td>
  </tr>
</table>

# Arbitrary color replacement on posterized images, based on a theme
## Example:
```python3 superwand.py examples/images/zebra.png 'Urban'```

Color themes included:
<table>
  <tr>
    <td><img src="/themes_jpgs/SpringTheme.jpg" alt="Image 1"></td>
    <td><img src="/themes_jpgs/SummerTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/WinterTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/FallTheme.jpg" alt="Image 2"></td>
    <td><img src="/themes_jpgs/ArcticTheme.jpg" alt="tropical">
  </tr>
  <tr>
    <td><img src="/themes_jpgs/SafariTheme.jpg" alt="Image 3"></td>
    <td><img src="/themes_jpgs/UrbanTheme.jpg" alt="Image 4"></td>
    <td><img src="/themes_jpgs/NeonTheme.jpg" alt="Image 4"></td>
    <td><img src="/themes_jpgs/TropicalTheme.jpg" alt="ADSF">
    <td><img src="/themes_jpgs/PaixãoTheme.jpg" alt="ADSF">
  </tr>
</table>

Examples applied to Charizard:

<table>
  <tr>
    <td><img src="/examples/charizards/Spring_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Summer_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Fall_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Winter_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Arctic_charizard.png" alt="Image 3"></td>
  </tr>
  <tr>
    <td><img src="/examples/charizards/Safari_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Urban_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Neon_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Tropical_charizard.png" alt="Image 3"></td>
    <td><img src="/examples/charizards/Paixão_charizard.png" alt="Image 3"></td>
  </tr>
</table>

See also, spring theme art:
<table>
  <tr>
    <td><img src="/examples/images/zebra.png" alt="Image 3"></td>
    <td><img src="/examples/images/Spring_zebra.png" alt="Image 3"></td>
  </tr>
  <tr>
    <td><img src="/examples/images/mantis_shrimp.jpeg" alt="Image 3"></td>
    <td><img src="/examples/images/Spring_mantis_shrimp.png" alt="Image 3"></td>
  </tr>
  <tr>
    <td><img src="/examples/images/obama.jpeg" alt="Image 3"></td>
    <td><img src="/examples/images/Fall_obama.png" alt="Image 3"></td>
  </tr>
</table>