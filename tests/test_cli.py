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


def test_k_sweep_writes_one_folder_per_k_and_a_sheet(tmp_path, quad_path):
    out = tmp_path / "sweep"
    assert run(quad_path, "-k", "2,3", "-t", "Neon,Arctic", "--sheet", "--out-dir", out, "-q") == 0
    assert sorted(p.name for p in (out / "k2").iterdir()) == ["quad_Arctic.png", "quad_Neon.png"]
    assert sorted(p.name for p in (out / "k3").iterdir()) == ["quad_Arctic.png", "quad_Neon.png"]
    assert Image.open(out / "quad_sheet.png").width > 2 * 200


def test_single_k_stays_flat(tmp_path, quad_path):
    assert run(quad_path, "-k", "3", "-t", "Neon", "-o", tmp_path, "-q") == 0
    assert (tmp_path / "quad_Neon.png").exists()
    assert not (tmp_path / "k3").exists()


def test_k_range_and_all_themes(tmp_path, quad_path):
    assert run(quad_path, "-k", "2-4", "-t", "all", "-o", tmp_path, "-q") == 0
    for k in (2, 3, 4):
        assert len(list((tmp_path / f"k{k}").glob("*.png"))) == len(color_themes)


def test_theme_list_vs_color_list(tmp_path, quad_path):
    assert run(quad_path, "-t", "neon,arctic", "-o", tmp_path, "-q") == 0
    assert {p.name for p in tmp_path.glob("*.png")} >= {"quad_Neon.png", "quad_Arctic.png"}
    assert run(quad_path, "-t", "red,blue", "-o", tmp_path, "-q") == 0
    assert (tmp_path / "quad_custom.png").exists()


def test_seed_makes_runs_repeatable(tmp_path):
    noise = np.random.default_rng(5).integers(0, 256, (40, 40, 3), dtype=np.uint8)
    src = tmp_path / "noise.png"
    Image.fromarray(noise).save(src)
    for name in ("a", "b"):
        assert run(src, "-t", "Neon", "-k", "12", "--seed", "3", "-o", tmp_path / name, "-q") == 0
    a = np.array(Image.open(tmp_path / "a" / "noise_Neon.png"))
    b = np.array(Image.open(tmp_path / "b" / "noise_Neon.png"))
    assert np.array_equal(a, b)


def test_sweep_skips_locks_where_the_region_does_not_exist(tmp_path, quad_path):
    assert run(quad_path, "-k", "2,4", "-t", "Neon", "--lock", "4", "-o", tmp_path, "-q") == 0
    k4 = np.array(Image.open(tmp_path / "k4" / "quad_Neon.png"))
    assert k4[39, 39, :3].tolist() == [250, 250, 250]  # region 4 (white) kept
    # With a single k a missing region is an error for that input
    assert run(quad_path, "-k", "2", "-t", "Neon", "--lock", "4", "-o", tmp_path) == 1


def test_sweep_palette_and_gif(tmp_path, quad_path, capsys):
    assert run(quad_path, "--palette", "-k", "2,4") == 0
    out = capsys.readouterr().out
    assert "k = 2:" in out and "k = 4:" in out
    with pytest.raises(SystemExit):
        run(quad_path, "--palette", tmp_path / "x.hex", "-k", "2,4")
    assert run(quad_path, "--gif", "-t", "Neon", "-k", "2,3", "-o", tmp_path, "-q") == 0
    assert (tmp_path / "k2" / "quad_themes.gif").exists()
    with pytest.raises(SystemExit):
        run(quad_path, "--gif", "--sheet")


def test_bad_k_values(quad_path):
    for bad in ("0", "2-", "x", "70"):
        with pytest.raises(SystemExit):
            run(quad_path, "-k", bad)
