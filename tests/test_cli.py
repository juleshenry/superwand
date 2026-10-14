import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from superwand import color_themes
from superwand.cli import CliError, css_main, expand_inputs, gradient_main, main, parse_overrides


def run(*argv):
    return main([str(a) for a in argv])


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        run("--version")
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("superwand ")


def test_list_themes(capsys, isolated_user_themes):
    isolated_user_themes.mkdir()
    (isolated_user_themes / "mine.hex").write_text("#010203\n")
    assert run("--list-themes") == 0
    out = capsys.readouterr().out
    assert all(name in out for name in color_themes)
    assert "mine" in out and "(user)" in out


def test_one_theme(tmp_path, quad_path, capsys):
    assert run(quad_path, "-t", "Urban", "-o", tmp_path / "out") == 0
    assert (tmp_path / "out" / "quad_Urban.png").exists()
    assert "Saved" in capsys.readouterr().out


def test_every_theme_by_default(tmp_path, quad_path):
    assert run(quad_path, "-k", "2", "-o", tmp_path, "-q") == 0
    assert len(list(tmp_path.glob("quad_*.png"))) == len(color_themes)


def test_old_single_dash_flags(tmp_path, quad_path, capsys):
    assert run(quad_path, "-theme", "Neon", "-gradient", "radial", "-o", tmp_path) == 0
    assert (tmp_path / "quad_Neon.png").exists()
    assert run(quad_path, "-theme", "Neon", "-tolerance", "40", "-o", tmp_path) == 0
    assert "-tolerance has no effect" in capsys.readouterr().err


def test_color_list_and_overrides(tmp_path, quad_path):
    args = [quad_path, "-t", "#ff0000,#00ff00,#0000ff,#ffff00", "-o", tmp_path]
    assert run(*args, "--lock", "1", "--map", "4=navy") == 0
    out = np.array(Image.open(tmp_path / "quad_custom.png"))
    assert out[0, 0, :3].tolist() == [0, 0, 0]  # region 1 (black) locked
    assert out[39, 39, :3].tolist() == [0, 0, 128]  # region 4 (white) mapped to navy


def test_rendering_flags(tmp_path, quad_path):
    for flags in (["--smooth"], ["--preserve-shading"], ["--flood"], ["--space", "rgb"]):
        assert run(quad_path, "-t", "Neon", "-o", tmp_path, "-q", *flags) == 0


def test_palette_from(tmp_path, quad_path):
    ref = tmp_path / "ref.png"
    Image.new("RGB", (8, 8), (200, 30, 30)).save(ref)
    assert run(quad_path, "--palette-from", ref, "-k", "1", "-o", tmp_path) == 0
    assert (tmp_path / "quad_from_ref.png").exists()


def test_gif(tmp_path, quad_path):
    assert run(quad_path, "--gif", "-t", "Neon", "-t", "Arctic", "-o", tmp_path) == 0
    with Image.open(tmp_path / "quad_themes.gif") as gif:
        assert gif.n_frames == 2


def test_palette_output(tmp_path, quad_path, capsys):
    assert run(quad_path, "--palette", "-k", "4") == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split()[:2] == ["1", "#000000"]
    assert lines[0].endswith("43.8%")

    assert run(quad_path, "--palette", "--format", "json", "-k", "4") == 0
    assert json.loads(capsys.readouterr().out)["colors"][0] == "#000000"

    target = tmp_path / "colors.ase"
    assert run(quad_path, "--palette", target) == 0
    assert target.read_bytes()[:4] == b"ASEF"

    with pytest.raises(SystemExit):
        run(quad_path, "--palette", "--format", "ase")


def test_text_inputs(tmp_path, capsys):
    css = tmp_path / "site.css"
    css.write_text(".a { color: #777; background: #888; }\n")
    svg = tmp_path / "logo.svg"
    svg.write_text('<svg><rect fill="#ff0000"/></svg>')
    assert run(css, svg, "-t", "#000000", "-o", tmp_path / "out", "--min-contrast", "4.5") == 0
    assert (tmp_path / "out" / "logo_custom.svg").read_text() == '<svg><rect fill="#000000"/></svg>'
    fixed = (tmp_path / "out" / "site_custom.css").read_text()
    assert "#000000" in fixed and "color: #000000" not in fixed
    assert "for contrast" in capsys.readouterr().err


def test_folder_input_and_jobs(tmp_path, quad_img):
    folder = tmp_path / "in"
    folder.mkdir()
    for name in ("a.png", "b.png"):
        quad_img.save(folder / name)
    (folder / "notes.txt").write_text("skip me")
    assert run(folder, "-t", "Neon", "-j", "2", "-o", tmp_path / "out", "-q") == 0
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["a_Neon.png", "b_Neon.png"]


def test_bad_inputs_fail_with_exit_codes(tmp_path, quad_path, capsys):
    with pytest.raises(SystemExit) as exc:
        run(tmp_path / "missing.png", "-t", "Neon")
    assert exc.value.code == 2
    with pytest.raises(SystemExit):
        run(quad_path, "-t", "NotATheme")
    with pytest.raises(SystemExit):
        run(quad_path, "--smooth", "--flood")
    with pytest.raises(SystemExit):
        run(quad_path, "--polarity", "2")
    with pytest.raises(SystemExit):
        run("-t", "Neon")  # theme without input

    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    assert run(broken, quad_path, "-t", "Neon", "-o", tmp_path) == 1
    err = capsys.readouterr().err
    assert "broken.png" in err and "error" in err
    assert (tmp_path / "quad_Neon.png").exists()  # the good input still ran


def test_no_inputs_launches_studio(monkeypatch):
    calls = []
    monkeypatch.setattr("superwand.cli.run_studio", lambda *a: calls.append(a) or 0)
    assert run("--port", "5050") == 0
    assert calls == [("127.0.0.1", 5050, False)]


def test_studio_without_flask(monkeypatch, capsys):
    from superwand.cli import run_studio

    monkeypatch.delitem(sys.modules, "superwand.studio.app", raising=False)
    monkeypatch.setitem(sys.modules, "flask", None)  # as if Flask weren't installed
    assert run_studio("127.0.0.1", 5001, False) == 1
    assert "pip install 'superwand[studio]'" in capsys.readouterr().err


def test_expand_inputs(tmp_path):
    (tmp_path / "a.png").write_bytes(b"")
    (tmp_path / "b.svg").write_text("")
    assert [p.name for p in expand_inputs([str(tmp_path / "*.png")])] == ["a.png"]
    assert [p.name for p in expand_inputs([str(tmp_path)])] == ["a.png", "b.svg"]
    with pytest.raises(CliError):
        expand_inputs([str(tmp_path / "*.jpg")])


def test_parse_overrides():
    assert parse_overrides([1], ["2=#ff0000"]) == {0: None, 1: (255, 0, 0)}
    for bad in (["x=#fff"], ["0=#fff"], ["2"], ["2=notacolor"]):
        with pytest.raises(CliError):
            parse_overrides([], bad)
    with pytest.raises(CliError):
        parse_overrides([0], [])


def test_gradient_enforce_cli(tmp_path, quad_path, capsys):
    out = tmp_path / "g.png"
    assert gradient_main([str(quad_path), "--style", "radial", "--output", str(out)]) == 0
    assert out.exists()
    args = [str(quad_path), "--color1", "#ff0000", "--color2", "0,0,255", "--output", str(out)]
    assert gradient_main(args) == 0
    assert gradient_main([str(tmp_path / "missing.png")]) == 1
    assert "error" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        gradient_main([str(quad_path), "--color1", "#ff0000"])
    assert gradient_main([str(quad_path), "--opacity", "x", "--output", str(out)]) == 0
    assert "no effect" in capsys.readouterr().err


def test_css_retheme_cli(tmp_path, capsys):
    css = tmp_path / "s.css"
    css.write_text(".a { color: #777; background: #888; }\n")
    assert css_main([str(css), "#000000"]) == 0
    assert "color: #000000" in capsys.readouterr().out
    assert css_main([str(css), "--check"]) == 1
    assert "1.2" in capsys.readouterr().out
    out = tmp_path / "o.css"
    assert css_main([str(css), "#000000", "--min-contrast", "4.5", "-o", str(out)]) == 0
    assert "adjusted" in capsys.readouterr().err
    assert css_main([str(tmp_path / "missing.css")]) == 1
    svg = tmp_path / "x.svg"
    svg.write_text('<svg fill="red"/>')
    assert css_main([str(svg), "Neon"]) == 0
    assert Path(svg).read_text() == '<svg fill="red"/>'  # input untouched
