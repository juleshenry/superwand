import base64
import io
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

pytest.importorskip("flask")

from superwand.studio import app as studio
from superwand.studio.app import StoredFile, UploadStore, build_targets, create_app

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def quad_png():
    """Four flat quadrants, opaque."""
    arr = np.zeros((40, 40, 3), dtype=np.uint8)
    arr[:20, 20:] = (200, 30, 30)
    arr[20:, :20] = (30, 200, 30)
    arr[20:, 20:] = (240, 240, 240)
    return png_bytes(arr)


@pytest.fixture
def sprite_png():
    """A sprite: two colors on a fully transparent background."""
    arr = np.zeros((30, 30, 4), dtype=np.uint8)
    arr[5:25, 5:15] = (200, 40, 40, 255)
    arr[5:25, 15:25] = (40, 40, 200, 255)
    return png_bytes(arr)


def upload(client, data, name):
    rv = client.post(
        "/upload", data={"file": (io.BytesIO(data), name)}, content_type="multipart/form-data"
    )
    return rv


def upload_id(client, data, name):
    rv = upload(client, data, name)
    assert rv.status_code == 200, rv.get_json()
    return rv.get_json()["filename"]


def decode(rv):
    assert rv.status_code == 200, rv.get_json()
    return np.array(Image.open(io.BytesIO(base64.b64decode(rv.get_json()["image"]))))


def test_index_uses_local_stylesheet(client):
    rv = client.get("/")
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert "SuperWand Studio" in html
    assert "/static/studio.css" in html
    assert "cdn.tailwindcss.com" not in html
    assert "Vaporwave" in html and "Preserve shading" in html and "Smooth edges" in html
    assert "Tolerance" not in html
    css = client.get("/static/studio.css")
    assert css.status_code == 200 and len(css.data) > 1000
    css.close()


def test_index_lists_user_themes(client, tmp_path, monkeypatch):
    monkeypatch.setenv("SUPERWAND_THEMES_DIR", str(tmp_path))
    (tmp_path / "Bubblegum.hex").write_text("#ff77aa\n#77aaff\n")
    assert "Bubblegum" in client.get("/").get_data(as_text=True)


def test_upload_and_process_round_trip(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    assert file_id.endswith("_quad.png")
    image = client.get(f"/image/{file_id}")
    assert image.status_code == 200 and image.mimetype == "image/png"

    rv = client.post(
        "/process",
        json={
            "image_name": file_id,
            "k": 4,
            "threshold": 50,  # pre-0.4 clients send this; it's ignored
            "apply_palette": True,
            "colors": [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]],
        },
    )
    out = decode(rv)
    data = rv.get_json()
    assert out.shape == (40, 40, 4)
    assert len(data["original_colors"]) == 4
    assert sum(data["region_shares"]) == pytest.approx(1.0)
    used = {tuple(c) for c in out[..., :3].reshape(-1, 3)}
    assert used <= {(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)}


def test_process_without_palette_keeps_original(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    out = decode(client.post("/process", json={"image_name": file_id, "k": 4}))
    original = np.array(Image.open(io.BytesIO(quad_png)))
    assert (out[..., :3] == original).all()


def test_transparent_png_keeps_alpha(client, sprite_png):
    file_id = upload_id(client, sprite_png, "sprite.png")
    rv = client.post(
        "/process",
        json={
            "image_name": file_id,
            "k": 2,
            "apply_palette": True,
            "colors": [[0, 255, 0], [255, 255, 0]],
        },
    )
    out = decode(rv)
    alpha_in = np.array(Image.open(io.BytesIO(sprite_png)))[..., 3]
    assert out.shape[2] == 4
    assert (out[..., 3] == alpha_in).all()
    visible = out[alpha_in > 0][:, :3]
    assert {tuple(c) for c in visible} == {(0, 255, 0), (255, 255, 0)}


@pytest.mark.parametrize(
    "options", [{"smooth": True}, {"shading": True}, {"smooth": True, "shading": True}]
)
def test_smooth_and_shading_accepted(client, quad_png, options):
    file_id = upload_id(client, quad_png, "quad.png")
    payload = {"image_name": file_id, "k": 4, "apply_palette": True, "colors": [[9, 9, 9]] * 4}
    out = decode(client.post("/process", json={**payload, **options}))
    assert out.shape == (40, 40, 4)


def test_gradients_per_region(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    rv = client.post(
        "/process",
        json={
            "image_name": file_id,
            "k": 4,
            "colors": [[[255, 0, 0], [0, 0, 255]], None, None, None],
            "gradient_styles": ["vertical", "none", "none", "none"],
            "gradient_polarities": [0.5, None, None, None],
        },
    )
    out = decode(rv)
    assert len({tuple(c) for c in out[..., :3].reshape(-1, 3)}) > 4


def test_flood_and_smooth_rejected(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    rv = client.post("/process", json={"image_name": file_id, "flood": True, "smooth": True})
    assert rv.status_code == 400
    assert "combined" in rv.get_json()["error"]


@pytest.mark.parametrize("k", [0, 33, "lots"])
def test_bad_k_rejected(client, quad_png, k):
    file_id = upload_id(client, quad_png, "quad.png")
    rv = client.post("/process", json={"image_name": file_id, "k": k})
    assert rv.status_code == 400
    assert "k" in rv.get_json()["error"]


def test_bad_inputs_rejected(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    assert client.post("/process", data="nope", content_type="text/plain").status_code == 400
    rv = client.post(
        "/process", json={"image_name": file_id, "colors": ["not-a-color"], "apply_palette": True}
    )
    assert rv.status_code == 400
    rv = client.post("/process", json={"image_name": file_id, "gradient_styles": ["sideways"]})
    assert rv.status_code == 400
    assert client.post("/process", json={}).status_code == 400


def test_unknown_ids_are_404(client):
    rv = client.post("/process", json={"image_name": "deadbeef_nope.png"})
    assert rv.status_code == 404
    assert "error" in rv.get_json()
    assert client.get("/image/deadbeef_nope.png").status_code == 404
    rv = client.post("/retheme_text", json={"filename": "deadbeef_nope.css"})
    assert rv.status_code == 404


def test_unsupported_upload(client):
    rv = upload(client, b"just some text", "notes.txt")
    assert rv.status_code == 400
    assert "Unsupported" in rv.get_json()["error"]
    assert upload(client, b"", "empty.png").status_code == 400
    rv = client.post("/upload", data={}, content_type="multipart/form-data")
    assert rv.status_code == 400


def test_oversized_upload_is_413_json(app, client):
    app.config["MAX_CONTENT_LENGTH"] = 1000
    rv = upload(client, b"x" * 5000, "big.png")
    assert rv.status_code == 413
    assert "too large" in rv.get_json()["error"]


def test_lru_evicts_by_count(quad_png):
    app = create_app(max_items=2)
    client = app.test_client()
    first = upload_id(client, quad_png, "a.png")
    second = upload_id(client, quad_png, "b.png")
    client.get(f"/image/{first}")  # touch: `first` is now most recent
    third = upload_id(client, quad_png, "c.png")
    store = app.extensions["superwand"]
    assert len(store) == 2
    assert first in store and third in store and second not in store
    assert client.get(f"/image/{second}").status_code == 404


def test_lru_evicts_by_bytes():
    store = UploadStore(max_items=10, max_bytes=250)
    for name in "abc":
        store.put(name, StoredFile(data=b"x" * 100, kind="css"))
    assert "a" not in store and "b" in store and "c" in store
    assert store.total_bytes <= 250
    # A single item over the cap is kept (it's the one the user just uploaded)
    store.put("huge", StoredFile(data=b"x" * 1000, kind="css"))
    assert len(store) == 1 and "huge" in store


def test_store_counts_cached_arrays(quad_png):
    app = create_app(max_items=10, max_bytes=10**9)
    client = app.test_client()
    file_id = upload_id(client, quad_png, "quad.png")
    item = app.extensions["superwand"].get(file_id)
    before = item.nbytes
    client.post("/process", json={"image_name": file_id, "k": 3})
    assert item.nbytes > before  # decoded pixels and labels are accounted for


def test_regions_cached_per_k(client, quad_png, monkeypatch):
    calls = []
    real = studio.regions_from_array

    def counting(*args, **kwargs):
        calls.append(args[2] if len(args) > 2 else kwargs.get("k"))
        return real(*args, **kwargs)

    monkeypatch.setattr(studio, "regions_from_array", counting)
    file_id = upload_id(client, quad_png, "quad.png")
    for k in (4, 4, 3, 4):
        assert client.post("/process", json={"image_name": file_id, "k": k}).status_code == 200
    assert calls == [4, 3]


def test_css_retheme(client):
    file_id = upload_id(client, b"body { color: #ff0000; }", "test.css")
    assert "test.css" in file_id
    rv = client.post("/retheme_text", json={"filename": file_id, "colors": [[0, 255, 0]]})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["kind"] == "css"
    assert "#00ff00" in data["text"]
    # The pre-0.4 route and response key still work
    rv = client.post("/retheme_css", json={"filename": file_id, "colors": [[0, 255, 0]]})
    assert "#00ff00" in rv.get_json()["css"]


def test_css_retheme_defaults_to_a_theme(client):
    file_id = upload_id(client, b"a { color: #123456; }", "a.css")
    rv = client.post("/retheme_text", json={"filename": file_id})
    assert rv.status_code == 200
    assert "#123456" not in rv.get_json()["text"]


def test_css_min_contrast(client):
    css = b".card { color: #333333; background: #ffffff; }"
    file_id = upload_id(client, css, "card.css")
    colors = [[200, 200, 255], [255, 255, 255]]
    plain = client.post("/retheme_text", json={"filename": file_id, "colors": colors}).get_json()
    assert plain["contrast_fixes"] == []
    rv = client.post(
        "/retheme_text", json={"filename": file_id, "colors": colors, "min_contrast": 4.5}
    )
    data = rv.get_json()
    assert rv.status_code == 200
    assert len(data["contrast_fixes"]) == 1
    fix = data["contrast_fixes"][0]
    assert fix["selector"] == ".card"
    assert fix["ratio_after"] >= 4.5
    assert fix["after"] in data["text"]
    bad = client.post("/retheme_text", json={"filename": file_id, "min_contrast": 50})
    assert bad.status_code == 400


def test_svg_retheme(client):
    svg = (
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        b'<rect fill="#ff0000" width="5" height="10"/>'
        b'<rect style="fill: blue" x="5" width="5" height="10"/></svg>'
    )
    file_id = upload_id(client, svg, "logo.svg")
    rv = client.post(
        "/retheme_text", json={"filename": file_id, "colors": [[0, 255, 0], [255, 255, 0]]}
    )
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["kind"] == "svg"
    assert "#ff0000" not in data["text"] and "blue" not in data["text"]
    assert "#00ff00" in data["text"] and "#ffff00" in data["text"]
    # SVG uploads are never served back as documents
    assert client.get(f"/image/{file_id}").status_code == 404
    # ...and can't be processed as images
    assert client.post("/process", json={"image_name": file_id}).status_code == 400


def test_text_upload_must_be_utf8(client):
    assert upload(client, b"\xff\xfe\x00bad", "bad.css").status_code == 400


def test_apply_gradient(client, quad_png):
    file_id = upload_id(client, quad_png, "quad.png")
    out = decode(client.post("/apply_gradient", json={"image_name": file_id, "style": "radial"}))
    assert out.shape[:2] == (40, 40)
    rv = client.post("/apply_gradient", json={"image_name": file_id, "style": "sideways"})
    assert rv.status_code == 400


@pytest.mark.parametrize(
    ("name", "k", "colors"),
    [
        ("curacao.jpg", 4, [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]),
        # Originally an AVIF mislabeled as .jpg; the upload is normalized to PNG
        ("whale.jpg", 2, [[0, 0, 0], [255, 255, 255]]),
    ],
)
def test_fixture_photos_upload_and_process(client, name, k, colors):
    data = (FIXTURES / name).read_bytes()
    file_id = upload_id(client, data, name)
    assert file_id.endswith(Path(name).stem + ".png")
    image = client.get(f"/image/{file_id}")
    assert image.status_code == 200 and image.mimetype == "image/png" and image.data
    rv = client.post(
        "/process", json={"image_name": file_id, "k": k, "apply_palette": True, "colors": colors}
    )
    assert rv.status_code == 200
    assert len(rv.get_json()["original_colors"]) == k


def test_build_targets_semantics():
    own = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    pair = [[10, 10, 10], [20, 20, 20]]
    # Palette on: picked color, gradient pair, or the region's own color when unpicked
    assert build_targets(own, [[9, 9, 9], pair], None, True) == [
        (9, 9, 9),
        ((10, 10, 10), (20, 20, 20)),
        (3, 3, 3),
    ]
    # Palette off: only gradient regions are repainted
    styles = ["none", "vertical", "radial"]
    assert build_targets(own, [[9, 9, 9], [8, 8, 8], pair], styles, False) == [
        None,
        (2, 2, 2),
        ((10, 10, 10), (20, 20, 20)),
    ]
    assert build_targets(own, [], None, False) == [None, None, None]


def test_create_app_has_no_import_side_effects():
    import logging

    assert not hasattr(studio, "app")
    root_handlers = list(logging.getLogger().handlers)
    create_app()
    assert list(logging.getLogger().handlers) == root_handlers


# ---- theme x k sweep --------------------------------------------------------


def _decode(b64):
    return np.array(Image.open(io.BytesIO(base64.b64decode(b64))))


def test_index_has_sweep_tab(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="tab-sweep"' in html and 'id="sweepGrid"' in html


def test_sweep_grid_matches_the_editor(client):
    arr = np.zeros((128, 128, 4), dtype=np.uint8)  # big enough to be downsampled
    arr[20:100, 20:64] = (200, 40, 40, 255)
    arr[20:100, 64:110] = (40, 40, 200, 255)
    arr[40:60, 30:50] = (240, 220, 60, 255)
    fid = upload_id(client, png_bytes(arr), "big_sprite.png")
    resp = client.post(
        "/sweep", json={"image_name": fid, "ks": "2-3", "themes": ["Neon", "Arctic"], "size": 64}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ks"] == [2, 3] and data["themes"] == ["Neon", "Arctic"]
    assert [(t["theme"], t["k"]) for t in data["tiles"]] == [
        ("Neon", 2),
        ("Arctic", 2),
        ("Neon", 3),
        ("Arctic", 3),
    ]
    tile = data["tiles"][1]
    small = _decode(tile["image"])
    assert small.shape[0] == 64
    # Opening the tile in the editor (its k and colors) reproduces it at full size
    colors = [[int(h[i : i + 2], 16) for i in (1, 3, 5)] for h in tile["colors"]]
    full = _decode(
        client.post(
            "/process", json={"image_name": fid, "k": 2, "apply_palette": True, "colors": colors}
        ).get_json()["image"]
    )
    step = full.shape[0] // small.shape[0]
    assert np.array_equal(full[::step, ::step], small)


def test_sweep_reuses_cached_regions(client, sprite_png, monkeypatch):
    fid = upload_id(client, sprite_png, "sprite.png")
    calls = []
    real = studio.regions_from_array
    monkeypatch.setattr(
        studio, "regions_from_array", lambda *a, **kw: calls.append(a[2]) or real(*a, **kw)
    )
    body = {"image_name": fid, "ks": [2, 3], "themes": ["Neon"]}
    assert client.post("/sweep", json=body).status_code == 200
    assert client.post("/sweep", json={**body, "themes": "all", "shading": True}).status_code == 200
    assert client.post("/process", json={"image_name": fid, "k": 3}).status_code == 200
    assert sorted(calls) == [2, 3]


@pytest.mark.parametrize(
    "bad",
    [
        {"ks": "0-3"},
        {"ks": [40]},
        {"ks": "x"},
        {"themes": ["Nope"]},
        {"themes": 5},
        {"themes": "all", "ks": "1-32"},
        {"match": "nope"},
        {"size": 5},
    ],
)
def test_sweep_rejects_bad_input(client, sprite_png, bad):
    fid = upload_id(client, sprite_png, "sprite.png")
    assert client.post("/sweep", json={"image_name": fid, **bad}).status_code == 400
