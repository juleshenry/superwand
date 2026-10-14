"""
The SuperWand Studio Flask app.

Uploads live in memory only, in a size-capped LRU store, and every image is
normalized to PNG on upload. Region clustering results are cached per image
and k, so dragging sliders doesn't re-cluster.
"""

from __future__ import annotations

import base64
import io
import logging
import threading
import uuid
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from flask import Flask, Response, current_app, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from ..color import RGB, parse_color, rgb_to_hex
from ..css import recolor_text
from ..gradients import GRADIENT_STYLES
from ..regions import Regions, U8Array, load_image, regions_from_array
from ..render import Target, gradient_enforce, paint
from ..themes import MATCH_MODES, all_themes

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 32 * 1024 * 1024
MAX_K = 32
TEXT_KINDS = {".css": "css", ".svg": "svg"}
REGION_CACHE_SIZE = 4  # k values remembered per image


class BadRequest(ValueError):
    """Invalid client input; answered with a 400 and the message."""


class NotFound(Exception):
    """A missing or expired upload; answered with a 404 and the message."""


@dataclass
class StoredFile:
    """One upload: PNG bytes for images, UTF-8 bytes for CSS/SVG, plus caches."""

    data: bytes
    kind: str  # "image", "css" or "svg"
    decoded: tuple[U8Array, U8Array | None] | None = None
    regions: OrderedDict[int, Regions] = field(default_factory=OrderedDict)

    @property
    def nbytes(self) -> int:
        size = len(self.data)
        if self.decoded is not None:
            rgb, alpha = self.decoded
            size += rgb.nbytes + (alpha.nbytes if alpha is not None else 0)
        return size + sum(r.labels.nbytes for r in self.regions.values())


class UploadStore:
    """Thread-safe LRU of uploads, capped by item count and total bytes (caches included)."""

    def __init__(self, max_items: int = 32, max_bytes: int = 512 * 1024 * 1024) -> None:
        self.max_items = max_items
        self.max_bytes = max_bytes
        self._items: OrderedDict[str, StoredFile] = OrderedDict()
        self._lock = threading.RLock()

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: object) -> bool:
        return key in self._items

    @property
    def total_bytes(self) -> int:
        with self._lock:
            return sum(item.nbytes for item in self._items.values())

    def put(self, key: str, item: StoredFile) -> None:
        with self._lock:
            self._items[key] = item
            self._items.move_to_end(key)
            self._evict()

    def get(self, key: str) -> StoredFile | None:
        with self._lock:
            item = self._items.get(key)
            if item is not None:
                self._items.move_to_end(key)
            return item

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def _evict(self) -> None:
        # The most recent item always stays, even if it alone exceeds max_bytes
        while len(self._items) > 1 and (
            len(self._items) > self.max_items or self.total_bytes > self.max_bytes
        ):
            evicted, _ = self._items.popitem(last=False)
            logger.debug("Evicted upload %s", evicted)

    def decoded(self, item: StoredFile) -> tuple[U8Array, U8Array | None]:
        """The upload as (rgb, alpha) arrays, decoded once."""
        decoded = item.decoded
        if decoded is None:
            decoded = load_image(Image.open(io.BytesIO(item.data)))
            with self._lock:
                item.decoded = decoded
                self._evict()
        return decoded

    def regions(self, item: StoredFile, k: int, compute: Callable[[], Regions]) -> Regions:
        """Regions for this upload and k, computed at most once while cached."""
        with self._lock:
            cached = item.regions.get(k)
            if cached is not None:
                item.regions.move_to_end(k)
                return cached
        found = compute()
        with self._lock:
            item.regions[k] = found
            while len(item.regions) > REGION_CACHE_SIZE:
                item.regions.popitem(last=False)
            self._evict()
        return found


def _store() -> UploadStore:
    store: UploadStore = current_app.extensions["superwand"]
    return store


def _payload() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("Expected a JSON object body")
    return data


def _lookup(data: dict[str, Any], key: str, kind: str | None = None) -> StoredFile:
    file_id = data.get(key)
    if not file_id:
        raise BadRequest(f"Missing {key}")
    item = _store().get(str(file_id))
    if item is None:
        raise NotFound("File not found; it may have expired, please upload it again")
    if kind == "image" and item.kind != "image":
        raise BadRequest("That upload is not an image")
    if kind == "text" and item.kind not in ("css", "svg"):
        raise BadRequest("That upload is not a CSS or SVG file")
    return item


def _int_param(data: dict[str, Any], key: str, default: int, lo: int, hi: int) -> int:
    try:
        value = int(data.get(key, default))
    except (TypeError, ValueError) as e:
        raise BadRequest(f"{key} must be an integer") from e
    if not lo <= value <= hi:
        raise BadRequest(f"{key} must be between {lo} and {hi}")
    return value


def _float_or_none(value: Any, key: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise BadRequest(f"{key} must be a number") from e


def _is_pair(color: Any) -> bool:
    return (
        isinstance(color, (list, tuple)) and len(color) == 2 and isinstance(color[0], (list, tuple))
    )


def _color(value: Any) -> RGB:
    try:
        return parse_color(value)
    except (TypeError, ValueError) as e:
        raise BadRequest(f"Invalid color {value!r}") from e


def build_targets(
    region_colors: list[RGB],
    colors: list[Any],
    gradient_styles: list[Any] | None,
    apply_palette: bool,
) -> list[Target]:
    """
    Per-region paint targets from the Studio's controls.

    With "Apply Color Palette" on, each region takes its picked color or
    gradient pair (regions without one are repainted in their own color).
    With it off, only regions with a gradient are repainted: from their picked
    pair, or from their own color; the rest keep their original pixels.
    """
    targets: list[Target] = []
    for i, own in enumerate(region_colors):
        color: Any = colors[i] if i < len(colors) else None
        pair = (_color(color[0]), _color(color[1])) if _is_pair(color) else None
        has_gradient = bool(
            gradient_styles
            and i < len(gradient_styles)
            and gradient_styles[i] not in (None, "none")
        )
        if apply_palette:
            targets.append(pair or (own if color is None else _color(color)))
        elif has_gradient:
            targets.append(pair or own)
        else:
            targets.append(None)
    return targets


def _png_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _image_from_arrays(rgb: U8Array, alpha: U8Array | None) -> Image.Image:
    if alpha is None:
        return Image.fromarray(rgb, "RGB")
    return Image.fromarray(np.dstack([rgb, alpha]), "RGBA")


def _normalize_image(data: bytes) -> bytes:
    """Re-encodes any Pillow-readable image (EXIF-rotated, alpha kept) as PNG."""
    with Image.open(io.BytesIO(data)) as img:
        rgb, alpha = load_image(img)
    buf = io.BytesIO()
    _image_from_arrays(rgb, alpha).save(buf, format="PNG")
    return buf.getvalue()


def index() -> str:
    return render_template("index.html", themes=all_themes())


def upload_file() -> tuple[Response, int] | Response:
    file = request.files.get("file")
    if file is None:
        raise BadRequest("No file part")
    if not file.filename:
        raise BadRequest("No selected file")
    name = secure_filename(file.filename) or "upload"
    data = file.read()
    if not data:
        raise BadRequest("Uploaded file is empty")

    stem, ext = Path(name).stem or "upload", Path(name).suffix.lower()
    kind = TEXT_KINDS.get(ext)
    if kind:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise BadRequest(f"{ext} files must be UTF-8 text") from e
        stored_name = name
    else:
        try:
            data = _normalize_image(data)
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as e:
            logger.info("Rejected upload %s: %s", name, e)
            raise BadRequest(
                "Unsupported file: upload an image (PNG, JPEG, WebP, AVIF, GIF, BMP, TIFF), "
                "a .css or an .svg file"
            ) from e
        kind = "image"
        stored_name = f"{stem}.png"

    file_id = f"{uuid.uuid4().hex}_{stored_name}"
    _store().put(file_id, StoredFile(data=data, kind=kind))
    return jsonify({"filename": file_id, "kind": kind})


def serve_image(filename: str) -> Response:
    item = _store().get(filename)
    if item is None or item.kind != "image":
        raise NotFound("Image not found")
    return send_file(
        io.BytesIO(item.data), mimetype="image/png", as_attachment=False, download_name=filename
    )


def process_image() -> Response:
    data = _payload()
    item = _lookup(data, "image_name", kind="image")
    k = _int_param(data, "k", 4, 1, MAX_K)
    flood, smooth, shading = (bool(data.get(key)) for key in ("flood", "smooth", "shading"))
    if flood and smooth:
        raise BadRequest("Flood and smooth edges can't be combined")
    apply_palette = bool(data.get("apply_palette"))
    colors = data.get("colors") or []
    styles = data.get("gradient_styles")
    polarities = data.get("gradient_polarities")
    if not isinstance(colors, list):
        raise BadRequest("colors must be a list")
    if styles is not None and not isinstance(styles, (list, str)):
        raise BadRequest("gradient_styles must be a list")
    if isinstance(polarities, list):
        polarities = [_float_or_none(p, "gradient_polarities") for p in polarities]
    else:
        polarities = _float_or_none(polarities, "gradient_polarities")

    store = _store()
    rgb, alpha = store.decoded(item)
    regions = store.regions(item, k, lambda: regions_from_array(rgb, alpha, k))
    style_list = [styles] * len(regions) if isinstance(styles, str) else styles
    targets = build_targets(list(regions.colors), colors, style_list, apply_palette)
    img = paint(
        rgb,
        alpha,
        regions,
        targets,
        gradient=styles,
        polarity=0.5 if polarities is None else polarities,
        flood=flood,
        smooth=smooth,
        shading=shading,
    )
    total = sum(regions.counts) or 1
    return jsonify(
        {
            "image": _png_base64(img),
            "original_colors": [list(c) for c in regions.colors],
            "region_shares": [count / total for count in regions.counts],
        }
    )


def retheme_text() -> Response:
    data = _payload()
    item = _lookup(data, "filename", kind="text")
    colors = data.get("colors") or []
    if not isinstance(colors, list):
        raise BadRequest("colors must be a list")
    palette: Any = [_color(c) for c in colors if c is not None] or data.get("theme") or "Tropical"
    match = data.get("match") or "order"
    if match not in MATCH_MODES:
        raise BadRequest(f"match must be one of {', '.join(MATCH_MODES)}")
    min_contrast = _float_or_none(data.get("min_contrast"), "min_contrast")
    if min_contrast is not None and not 1 <= min_contrast <= 21:
        raise BadRequest("min_contrast must be between 1 and 21")

    result = recolor_text(
        item.data.decode("utf-8"),
        palette,
        kind=item.kind,
        match=match,
        min_contrast=min_contrast if item.kind == "css" else None,
    )
    fixes = [
        {
            "selector": fix.selector,
            "before": rgb_to_hex(fix.before),
            "after": rgb_to_hex(fix.after),
            "background": rgb_to_hex(fix.background),
            "ratio_before": round(fix.ratio_before, 2),
            "ratio_after": round(fix.ratio_after, 2),
        }
        for fix in result.contrast_fixes
    ]
    return jsonify(
        {"text": result.text, "css": result.text, "kind": item.kind, "contrast_fixes": fixes}
    )


def apply_gradient_route() -> Response:
    data = _payload()
    item = _lookup(data, "image_name", kind="image")
    style = data.get("style") or "auto"
    if style not in GRADIENT_STYLES or style == "none":
        raise BadRequest(f"Unsupported gradient style {style!r}")
    k = _int_param(data, "k", 4, 1, MAX_K)
    rgb, alpha = _store().decoded(item)
    img = gradient_enforce(_image_from_arrays(rgb, alpha), style=style, number=k)
    return jsonify({"image": _png_base64(img)})


def _error(message: str, status: int) -> tuple[Response, int]:
    return jsonify({"error": message}), status


def create_app(max_items: int = 32, max_bytes: int = 512 * 1024 * 1024) -> Flask:
    """Builds a Studio app with its own in-memory upload store."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    app.extensions["superwand"] = UploadStore(max_items=max_items, max_bytes=max_bytes)

    app.add_url_rule("/", view_func=index)
    app.add_url_rule("/upload", view_func=upload_file, methods=["POST"])
    app.add_url_rule("/image/<path:filename>", view_func=serve_image)
    app.add_url_rule("/process", view_func=process_image, methods=["POST"])
    app.add_url_rule("/retheme_text", view_func=retheme_text, methods=["POST"])
    app.add_url_rule(
        "/retheme_css", endpoint="retheme_css", view_func=retheme_text, methods=["POST"]
    )
    app.add_url_rule("/apply_gradient", view_func=apply_gradient_route, methods=["POST"])

    @app.errorhandler(BadRequest)
    def bad_request(e: BadRequest) -> tuple[Response, int]:
        return _error(str(e), 400)

    @app.errorhandler(NotFound)
    def not_found(e: NotFound) -> tuple[Response, int]:
        return _error(str(e), 404)

    @app.errorhandler(HTTPException)
    def http_error(e: HTTPException) -> tuple[Response, int]:
        if e.code == 413:
            limit = (app.config["MAX_CONTENT_LENGTH"] or 0) // (1024 * 1024)
            return _error(f"File too large (limit {limit} MB)", 413)
        return _error(e.description or e.name, e.code or 500)

    @app.errorhandler(Exception)
    def server_error(e: Exception) -> tuple[Response, int]:
        if isinstance(e, ValueError):  # bad parameters caught deeper in the pipeline
            return _error(str(e), 400)
        logger.exception("Studio request failed")
        return _error(f"Internal error: {e}", 500)

    return app
