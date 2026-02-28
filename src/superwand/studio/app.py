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

import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import numpy as np
from ..core.np_region_identifier import (
    np_get_prominent_regions,
    np_inject_theme_image,
)
from ..utils.css_rethemer import css_retheme
from ..utils.gradients import gradient_enforce
from ..core.np_themes import CORES_DOIS as CORES

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# In-memory storage for uploaded files during the session
in_memory_storage = {}


@app.route("/")
def index():
    return render_template("index.html", themes=CORES)


@app.route("/process", methods=["POST"])
def process_image():
    data = request.json
    image_name = data.get("image_name")
    if not image_name:
        return jsonify({"error": "No image selected"}), 400

    file_bytes = in_memory_storage.get(image_name)
    if not file_bytes:
        return jsonify({"error": "Image not found in memory"}), 404

    # Parameters
    k = int(data.get("k", 4))
    threshold = int(data.get("threshold", 50))
    flood = data.get("flood", False)
    apply_palette = data.get("apply_palette", False)
    gradient_styles = data.get("gradient_styles")
    gradient_polarities = data.get("gradient_polarities")
    colors = data.get("colors", [])  # List of [r, g, b] or [[r, g, b], [r, g, b]]

    # Process
    try:
        # Get regions
        regions = np_get_prominent_regions(io.BytesIO(file_bytes), number=k, tolerance=threshold)

        # Prepare theme colors
        theme_rgbs = []
        region_keys = list(regions.keys())
        for i in range(len(region_keys)):
            if i < len(colors):
                color = colors[i]
                if not apply_palette:
                    if (
                        gradient_styles
                        and i < len(gradient_styles)
                        and gradient_styles[i] != "none"
                    ):
                        if (
                            isinstance(color, list)
                            and len(color) > 0
                            and isinstance(color[0], list)
                        ):
                            theme_rgbs.append((tuple(color[0]), tuple(color[1])))
                        else:
                            theme_rgbs.append(region_keys[i])
                    else:
                        theme_rgbs.append(None)
                else:
                    if color is None:
                        theme_rgbs.append(region_keys[i])
                    elif (
                        isinstance(color, list)
                        and len(color) > 0
                        and isinstance(color[0], list)
                    ):
                        theme_rgbs.append((tuple(color[0]), tuple(color[1])))
                    else:
                        theme_rgbs.append(tuple(color))
            else:
                theme_rgbs.append(region_keys[i] if apply_palette else None)

        # Inject theme
        original_img = Image.open(io.BytesIO(file_bytes))
        original_img = ImageOps.exif_transpose(original_img)
        processed_img = np_inject_theme_image(
            regions,
            theme_rgbs,
            original_img,
            flood=flood,
            gradient_styles=gradient_styles,
            gradient_polarities=gradient_polarities,
        )

        # Convert to base64 for live display
        buffered = io.BytesIO()
        processed_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify(
            {"image": img_str, "original_colors": [list(c) for c in regions.keys()]}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/retheme_css", methods=["POST"])
def retheme_css_route():
    data = request.json
    filename = data.get("filename")
    colors = data.get("colors", [])

    if not filename:
        return jsonify({"error": "No CSS file selected"}), 400

    file_bytes = in_memory_storage.get(filename)
    if not file_bytes:
        return jsonify({"error": "File not found in memory"}), 404

    try:
        custom_theme = [tuple(c) for c in colors]
        modified_css = css_retheme(io.BytesIO(file_bytes), custom_theme=custom_theme)
        return jsonify({"css": modified_css})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/apply_gradient", methods=["POST"])
def apply_gradient_route():
    data = request.json
    image_name = data.get("image_name")
    style = data.get("style", "auto")

    if not image_name:
        return jsonify({"error": "No image selected"}), 400

    file_bytes = in_memory_storage.get(image_name)
    if not file_bytes:
        return jsonify({"error": "Image not found in memory"}), 404

    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        processed_img = gradient_enforce(img, style=style)

        buffered = io.BytesIO()
        processed_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({"image": img_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    
    # Ensure we're at the beginning of the stream and read all bytes
    file.seek(0)
    file_bytes = file.read()
    
    if not file_bytes:
        return jsonify({"error": "Uploaded file is empty"}), 400
        
    in_memory_storage[filename] = file_bytes

    return jsonify({"filename": filename})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
