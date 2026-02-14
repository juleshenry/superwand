import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from superwand.np_region_identifier import (
    np_get_prominent_regions,
    np_inject_theme_image,
)
from superwand.css_rethemer import css_retheme
from superwand.gradients import gradient_enforce
from superwand.__np_color_themes__ import CORES_DOIS as CORES

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "studio/static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html", themes=CORES)


@app.route("/process", methods=["POST"])
def process_image():
    data = request.json
    image_name = data.get("image_name")
    if not image_name:
        return jsonify({"error": "No image selected"}), 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    # Parameters
    k = int(data.get("k", 4))
    threshold = int(data.get("threshold", 50))
    flood = data.get("flood", False)
    gradient_styles = data.get("gradient_styles")
    gradient_intensities = data.get("gradient_intensities")
    colors = data.get("colors", [])  # List of [r, g, b] or [[r, g, b], [r, g, b]]

    # Process
    try:
        # Get regions
        regions = np_get_prominent_regions(image_path, number=k, tolerance=threshold)

        # Prepare theme colors
        # If user provided colors, use them.
        theme_rgbs = []
        for i in range(len(regions)):
            if i < len(colors):
                color = colors[i]
                if isinstance(color[0], list):
                    theme_rgbs.append((tuple(color[0]), tuple(color[1])))
                else:
                    theme_rgbs.append(tuple(color))
            else:
                theme_rgbs.append((0, 0, 0))

        # Inject theme
        original_img = Image.open(image_path)
        processed_img = np_inject_theme_image(
            regions,
            theme_rgbs,
            original_img,
            flood=flood,
            gradient_styles=gradient_styles,
            gradient_intensities=gradient_intensities,
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

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        custom_theme = [tuple(c) for c in colors]
        modified_css = css_retheme(file_path, custom_theme=custom_theme)
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

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    try:
        img = Image.open(image_path).convert("RGB")
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
    file_path = os.path.join(str(app.config["UPLOAD_FOLDER"]), filename)
    file.save(file_path)

    return jsonify({"filename": filename})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
