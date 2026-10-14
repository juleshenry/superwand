"""Command-line entry points: `superwand`, `gradient-enforce` and `css-retheme`."""

from __future__ import annotations

import argparse
import glob
import os
import sys
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from .color import parse_color, rgb_to_hex
from .gradients import GRADIENT_STYLES
from .palette_io import FORMATS, dumps_palette, save_palette
from .regions import SPACES, find_regions, load_image, regions_from_array
from .themes import (
    MATCH_MODES,
    all_themes,
    color_themes,
    find_theme,
    resolve_theme,
    theme_label,
)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".avif"}
TEXT_KINDS = {".css": "css", ".svg": "svg"}
SHEET_CELL = 200  # contact sheet tile size in pixels
INPUT_EXTENSIONS = IMAGE_EXTENSIONS | set(TEXT_KINDS)

EXAMPLES = """\
examples:
  superwand                                   launch SuperWand Studio (needs superwand[studio])
  superwand art.png -t Vaporwave              one theme
  superwand art.png                           every theme, one file each
  superwand photo.jpg -t Fall --preserve-shading --smooth
  superwand logo.svg site.css -t "#ff0080,#00ffff,#1a0033"
  superwand rocket.png --palette-from shrimp.jpg -k 6
  superwand art.png --palette                 list regions (numbered for --lock/--map)
  superwand art.png -t Neon --lock 1 --map 2=hotpink
  superwand sprites/ -t Arctic -j 4 -o out/   a whole folder, in parallel
  superwand art.png -k 2-8 --sheet -o sweep/   every theme at k = 2..8, plus a theme x k grid
  superwand art.png -t Neon,Arctic -k 2,4,8    two themes at three k values
"""


class CliError(Exception):
    """A user-facing error; printed without a traceback."""


def _version() -> str:
    from . import __version__

    return __version__


def _warn(msg: str) -> None:
    print(f"superwand: warning: {msg}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="superwand",
        description="Retheme images, SVG and CSS with color palettes and gradients. "
        "Run with no inputs to launch SuperWand Studio.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    p.add_argument(
        "inputs",
        nargs="*",
        metavar="INPUT",
        help="images, .svg or .css files, folders, or glob patterns",
    )
    p.add_argument("-V", "--version", action="version", version=f"superwand {_version()}")

    g = p.add_argument_group("theme")
    g.add_argument(
        "-t",
        "--theme",
        action="append",
        metavar="THEME",
        help="theme name, comma list of names, 'all', palette file (.json .toml .gpl .ase "
        ".hex .txt .css), or colors like '#ff0080,#00ffff'; repeatable. Default: all",
    )
    g.add_argument(
        "--palette-from",
        metavar="IMAGE",
        help="use the k dominant colors of another image as the theme",
    )
    g.add_argument(
        "--match",
        choices=MATCH_MODES,
        help="pair regions with colors by prominence ('order', default for themes) or "
        "brightness ('luminance', default for --palette-from)",
    )
    g.add_argument("--list-themes", action="store_true", help="list themes and exit")

    r = p.add_argument_group("regions")
    r.add_argument(
        "-k",
        type=_k_arg,
        default=[4],
        metavar="K",
        help="number of color regions: 4, a list like 2,3,4,6,8, or a range like 2-8 "
        "(default 4). With several values, results go to k<N>/ subfolders",
    )
    r.add_argument(
        "--seed", type=int, default=42, help="k-means seed; same seed, same result (default 42)"
    )
    r.add_argument(
        "--space", choices=SPACES, default="oklab", help="color space for finding regions"
    )
    r.add_argument(
        "--lock",
        type=int,
        action="append",
        default=[],
        metavar="N",
        help="keep region N's original pixels (regions are numbered from 1, largest first)",
    )
    r.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="N=COLOR",
        help="paint region N with COLOR, e.g. 2=#ff0080 or 3=navy",
    )

    s = p.add_argument_group("rendering")
    s.add_argument("--gradient", choices=GRADIENT_STYLES, default="none", help="gradient style")
    s.add_argument(
        "--polarity",
        type=float,
        default=0.5,
        help="where along the gradient the 50/50 blend lands, 0..1 (default 0.5)",
    )
    s.add_argument("--flood", action="store_true", help="close holes and grow regions")
    s.add_argument("--smooth", action="store_true", help="blend colors across region edges")
    s.add_argument(
        "--preserve-shading",
        dest="shading",
        action="store_true",
        help="keep each pixel's light and shadow (best for photos)",
    )
    s.add_argument(
        "--min-contrast",
        type=float,
        metavar="RATIO",
        help="CSS: fix text colors below this WCAG contrast with their background (e.g. 4.5)",
    )

    o = p.add_argument_group("output")
    o.add_argument(
        "-o",
        "--output-dir",
        "--out-dir",
        dest="output_dir",
        default=".",
        help="output folder (default: current)",
    )
    o.add_argument(
        "--sheet",
        action="store_true",
        help="also write <name>_sheet.png, a labelled grid with themes as rows and k as columns",
    )
    o.add_argument("--gif", action="store_true", help="write an animated GIF cycling the themes")
    o.add_argument("--delay", type=int, default=700, help="GIF frame time in ms (default 700)")
    o.add_argument(
        "--palette",
        nargs="?",
        const="-",
        metavar="FILE",
        help="print the image's k dominant colors, or save them to FILE, and exit",
    )
    o.add_argument(
        "--format",
        choices=("text", *FORMATS),
        help="palette format (default: text on screen, else from the file extension)",
    )
    o.add_argument("-j", "--jobs", type=int, default=1, help="process inputs in parallel")
    o.add_argument("-q", "--quiet", action="store_true", help="only print errors")

    st = p.add_argument_group("studio")
    st.add_argument("--host", default="127.0.0.1", help="studio host (default 127.0.0.1)")
    st.add_argument("--port", type=int, default=5001, help="studio port (default 5001)")
    st.add_argument("--debug", action="store_true", help="run the studio in Flask debug mode")

    # Pre-0.4 spellings, still accepted but hidden from --help
    hide = argparse.SUPPRESS
    p.add_argument("-theme", dest="theme", action="append", help=hide)
    p.add_argument("-palette-from", dest="palette_from", help=hide)
    p.add_argument("-match", dest="match", choices=MATCH_MODES, help=hide)
    p.add_argument("-gradient", dest="gradient", choices=GRADIENT_STYLES, help=hide)
    p.add_argument("-polarity", dest="polarity", type=float, help=hide)
    p.add_argument("-flood", dest="flood", action="store_true", help=hide)
    p.add_argument("-gif", dest="gif", action="store_true", help=hide)
    p.add_argument("-palette", dest="palette", action="store_const", const="-", help=hide)
    p.add_argument("-tolerance", dest="tolerance", type=int, help=hide)
    p.add_argument("--headless", action="store_true", help=hide)
    return p


def _k_arg(value: str) -> list[int]:
    from .sweep import parse_k_values

    try:
        return parse_k_values(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from e


def expand_themes(values: Sequence[str] | None) -> list[str] | None:
    """-t values: 'all', comma lists of theme names, or any single theme (name, file, colors)."""
    if not values:
        return None
    out: list[str] = []
    for value in values:
        if value.strip().casefold() == "all":
            out.extend(all_themes())
            continue
        parts = [part.strip() for part in value.split(",") if part.strip()]
        found = [find_theme(part) for part in parts]
        if len(parts) > 1 and all(found):
            out.extend(f[0] for f in found if f)
        else:
            out.append(value)
    return list(dict.fromkeys(out))


def expand_inputs(patterns: Sequence[str]) -> list[Path]:
    """Files as given, folders expanded to the images/SVG/CSS inside, globs expanded."""
    found: list[Path] = []
    for pattern in patterns:
        path = Path(pattern).expanduser()
        if path.is_dir():
            found.extend(sorted(f for f in path.iterdir() if f.suffix.lower() in INPUT_EXTENSIONS))
        elif path.exists():
            found.append(path)
        elif glob.has_magic(pattern):
            matches = sorted(Path(m) for m in glob.glob(os.path.expanduser(pattern)))
            if not matches:
                raise CliError(f"no files match {pattern!r}")
            found.extend(m for m in matches if m.is_file())
        else:
            raise CliError(f"no such file: {pattern}")
    return found


def parse_overrides(locks: Sequence[int], maps: Sequence[str]) -> dict[int, Any]:
    """--lock N / --map N=COLOR (1-based) to retheme()'s 0-based overrides."""
    overrides: dict[int, Any] = {}
    for n in locks:
        if n < 1:
            raise CliError(f"--lock {n}: regions are numbered from 1")
        overrides[n - 1] = None
    for item in maps:
        index, sep, color = item.partition("=")
        if not sep or not index.strip().isdigit() or int(index) < 1:
            raise CliError(f"--map {item!r}: expected N=COLOR with N >= 1, e.g. 2=#ff0080")
        try:
            overrides[int(index) - 1] = parse_color(color)
        except ValueError as e:
            raise CliError(f"--map {item!r}: {e}") from e
    return overrides


def _themes(opts: dict[str, Any], k: int) -> list[Any]:
    if opts["palette_from"]:
        from .regions import extract_palette

        return [extract_palette(opts["palette_from"], k, seed=opts["seed"])]
    return list(opts["theme"] or all_themes())


def _label(theme: Any, opts: dict[str, Any]) -> str:
    if opts["palette_from"]:
        return f"from_{Path(opts['palette_from']).stem}"
    return theme_label(theme)


def process_input(path: Path, opts: dict[str, Any]) -> list[str]:
    """Rethemes one input with every requested theme; returns the saved paths."""
    from .css import recolor_text
    from .render import render_theme
    from .sweep import SweepTile, contact_sheet

    out_dir = Path(opts["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    default_match = "luminance" if opts["palette_from"] else "order"
    match = opts["match"] or default_match
    ks: list[int] = opts["k"]
    multi_k = len(ks) > 1

    def folder(k: int) -> Path:
        """One subfolder per k when sweeping several values, else the output folder."""
        target = out_dir / f"k{k}" if multi_k else out_dir
        target.mkdir(parents=True, exist_ok=True)
        return target

    kind = TEXT_KINDS.get(path.suffix.lower())
    if kind:  # k plays no part in CSS/SVG, so text inputs render once
        text = path.read_text(encoding="utf-8")
        for theme in _themes(opts, ks[0]):
            result = recolor_text(
                text, theme, kind=kind, match=match, min_contrast=opts["min_contrast"]
            )
            out = out_dir / f"{path.stem}_{_label(theme, opts)}{path.suffix}"
            out.write_text(result.text, encoding="utf-8")
            saved.append(str(out))
            for fix in result.contrast_fixes:
                _warn(
                    f"{out.name}: {fix.selector}: text {rgb_to_hex(fix.before)} -> "
                    f"{rgb_to_hex(fix.after)} for contrast {fix.ratio_after:.1f}:1"
                )
        return saved

    render_opts = {
        "gradient": opts["gradient"],
        "polarity": opts["polarity"],
        "smooth": opts["smooth"],
        "shading": opts["shading"],
    }
    if opts["gif"]:
        from .gif import theme_cycle_gif

        for k in ks:
            out = folder(k) / f"{path.stem}_themes.gif"
            theme_cycle_gif(
                path,
                out,
                themes=_themes(opts, k),
                k=k,
                delay=opts["delay"],
                match=match,
                overrides=_overrides_for(opts["overrides"], k, multi_k),
                **render_opts,
            )
            saved.append(str(out))
        return saved

    rgb, alpha = load_image(path)
    tiles: list[SweepTile] = []
    for k in ks:
        regions = regions_from_array(rgb, alpha, k, seed=opts["seed"], space=opts["space"])
        overrides = _overrides_for(opts["overrides"], len(regions), multi_k)
        for theme in _themes(opts, k):
            img = render_theme(
                rgb,
                alpha,
                regions,
                theme,
                match=match,
                overrides=overrides,
                flood=opts["flood"],
                **render_opts,
            )
            label = _label(theme, opts)
            out = folder(k) / f"{path.stem}_{label}.png"
            img.save(out)
            saved.append(str(out))
            if opts["sheet"]:
                img.thumbnail((SHEET_CELL, SHEET_CELL), Image.Resampling.LANCZOS)
                tiles.append(SweepTile(label, k, img))
    if tiles:
        out = out_dir / f"{path.stem}_sheet.png"
        contact_sheet(tiles, cell=SHEET_CELL, title=path.name).save(out)
        saved.append(str(out))
    return saved


def _overrides_for(overrides: dict[int, Any], n_regions: int, lenient: bool) -> dict[int, Any]:
    """In a k sweep, --lock/--map only apply at the k values that have that region."""
    if not lenient:
        return overrides
    return {i: color for i, color in overrides.items() if i < n_regions}


def _run_one(path: Path, opts: dict[str, Any]) -> tuple[Path, list[str], str | None]:
    try:
        return path, process_input(path, opts), None
    except (OSError, ValueError, IndexError, UnidentifiedImageError) as e:
        return path, [], str(e)


def print_palette(
    path: Path, k: int, target: str, fmt: str | None, space: str, seed: int = 42
) -> None:
    regions = find_regions(path, k, space=space, seed=seed)
    colors = regions.colors
    if target != "-":
        save_palette(colors, target, None if fmt in (None, "text") else fmt, path.stem)
        print(f"Saved {target}")
        return
    if fmt in (None, "text"):
        total = sum(regions.counts) or 1
        for i, (c, count) in enumerate(zip(colors, regions.counts, strict=True), 1):
            print(f"{i:>3}  {rgb_to_hex(c)}  rgb{c!s:<16} {100 * count / total:5.1f}%")
        return
    data = dumps_palette(colors, fmt, path.stem)
    if isinstance(data, bytes):
        raise CliError("--format ase is binary; save it to a file: --palette colors.ase")
    sys.stdout.write(data)


def list_themes() -> None:
    builtin = set(color_themes)
    for name, colors in all_themes().items():
        tag = "" if name in builtin else "  (user)"
        print(f"{name:<12} " + " ".join(rgb_to_hex(c) for c in colors) + tag)


def run_studio(host: str, port: int, debug: bool) -> int:
    try:
        from .studio.app import create_app
    except ImportError as e:
        if "flask" not in str(e).lower():
            raise
        print(
            "superwand: SuperWand Studio needs Flask. Install it with:\n"
            "  pip install 'superwand[studio]'",
            file=sys.stderr,
        )
        return 1
    from ._banner import BANNER

    print(BANNER)
    print(f"SuperWand Studio running at http://{host}:{port}  (Ctrl+C to stop)")
    create_app().run(host=host, port=port, debug=debug)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _main(parser, args)
    except CliError as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        return 130


def _main(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    if args.tolerance is not None:
        _warn("-tolerance has no effect and will be removed in 0.5")
    if args.list_themes:
        list_themes()
        return 0

    inputs = expand_inputs(args.inputs)
    if not inputs:
        if args.theme or args.palette_from or args.gif or args.palette or args.headless:
            raise CliError("an input file is required")
        if args.inputs:
            raise CliError("no images, .svg or .css files found in the given folders")
        return run_studio(args.host, args.port, args.debug)

    if not 0 <= args.polarity <= 1:
        raise CliError("--polarity must be between 0 and 1")
    if args.flood and args.smooth:
        raise CliError("--flood and --smooth can't be combined")
    if args.jobs < 1:
        raise CliError("--jobs must be at least 1")
    if args.sheet and args.gif:
        raise CliError("--sheet can't be combined with --gif")
    themes = expand_themes(args.theme)
    try:
        for theme in themes or []:
            resolve_theme(theme)
    except ValueError as e:
        raise CliError(str(e)) from e

    if args.palette:
        if args.palette != "-" and (len(inputs) > 1 or len(args.k) > 1):
            raise CliError("--palette FILE takes a single input and a single -k")
        for path in inputs:
            if len(inputs) > 1:
                print(f"{path}:")
            for k in args.k:
                if len(args.k) > 1:
                    print(f"k = {k}:")
                print_palette(path, k, args.palette, args.format, args.space, args.seed)
        return 0

    opts = {
        "theme": themes,
        "palette_from": args.palette_from,
        "match": args.match,
        "k": args.k,
        "seed": args.seed,
        "sheet": args.sheet,
        "space": args.space,
        "overrides": parse_overrides(args.lock, args.map),
        "gradient": None if args.gradient in (None, "none") else args.gradient,
        "polarity": args.polarity,
        "flood": args.flood,
        "smooth": args.smooth,
        "shading": args.shading,
        "min_contrast": args.min_contrast,
        "output_dir": args.output_dir,
        "gif": args.gif,
        "delay": args.delay,
    }

    failures = 0
    results: Iterable[tuple[Path, list[str], str | None]]
    if args.jobs > 1 and len(inputs) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(_run_one, inputs, [opts] * len(inputs)))
    else:
        results = (_run_one(path, opts) for path in inputs)
    for path, saved, error in results:
        if error:
            failures += 1
            print(f"superwand: error: {path}: {error}", file=sys.stderr)
        elif not args.quiet:
            for out in saved:
                print(f"Saved {out}")
    return 1 if failures else 0


def gradient_main(argv: Sequence[str] | None = None) -> int:
    """`gradient-enforce`: turn flat color regions into gradients."""
    from .render import gradient_enforce

    p = argparse.ArgumentParser(
        prog="gradient-enforce",
        description="Turn an image's flat color regions into gradients.",
        allow_abbrev=False,
    )
    p.add_argument("image_path", help="input image")
    p.add_argument(
        "--style",
        default="auto",
        choices=[s for s in GRADIENT_STYLES if s != "none"],
        help="gradient direction (default auto = top-down)",
    )
    p.add_argument("--polarity", type=float, default=0.5, help="midpoint bias, 0..1")
    p.add_argument("--color1", help="start color, e.g. '#ff0000' or '255,0,0'")
    p.add_argument("--color2", help="end color, e.g. '#0000ff' or '0,0,255'")
    p.add_argument("-k", "--number", type=int, default=4, help="regions (default 4)")
    p.add_argument("--output", help="output path (default gradient_<style>_<name>.png)")
    p.add_argument("--completeness", help=argparse.SUPPRESS)
    p.add_argument("--opacity", help=argparse.SUPPRESS)
    args = p.parse_args(argv)

    if args.completeness or args.opacity:
        _warn("--completeness and --opacity have no effect and will be removed in 0.5")
    if bool(args.color1) != bool(args.color2):
        p.error("--color1 and --color2 must be given together")
    try:
        c1 = parse_color(args.color1) if args.color1 else None
        c2 = parse_color(args.color2) if args.color2 else None
        img = gradient_enforce(
            args.image_path,
            style=args.style,
            color1=c1,
            color2=c2,
            polarity=args.polarity,
            number=args.number,
        )
        out = args.output or f"gradient_{args.style}_{Path(args.image_path).stem}.png"
        img.save(out)
    except (OSError, ValueError, UnidentifiedImageError) as e:
        print(f"gradient-enforce: error: {e}", file=sys.stderr)
        return 1
    print(f"Saved {out}")
    return 0


def css_main(argv: Sequence[str] | None = None) -> int:
    """`css-retheme`: retheme every color in a CSS or SVG file."""
    from .css import check_contrast, read_source, recolor_text

    p = argparse.ArgumentParser(
        prog="css-retheme",
        description="Retheme every color in a CSS or SVG file.",
        allow_abbrev=False,
    )
    p.add_argument("path", help="input .css or .svg file")
    p.add_argument("theme", nargs="?", default="Tropical", help="theme, palette file or colors")
    p.add_argument("--match", choices=MATCH_MODES, default="order", help="color pairing")
    p.add_argument("--min-contrast", type=float, metavar="RATIO", help="fix unreadable text")
    p.add_argument(
        "--check",
        action="store_true",
        help="report text/background pairs below --min-contrast (default 4.5) and exit",
    )
    p.add_argument("-o", "--output", help="output path (default: stdout)")
    args = p.parse_args(argv)

    kind = "svg" if args.path.lower().endswith(".svg") else "css"
    try:
        text = read_source(args.path)
        if args.check:
            issues = check_contrast(text, args.min_contrast or 4.5)
            for issue in issues:
                print(
                    f"{issue.selector}: {rgb_to_hex(issue.fg)} on {rgb_to_hex(issue.bg)} "
                    f"= {issue.ratio:.2f}:1"
                )
            return 1 if issues else 0
        result = recolor_text(
            text, args.theme, kind=kind, match=args.match, min_contrast=args.min_contrast
        )
    except (OSError, ValueError) as e:
        print(f"css-retheme: error: {e}", file=sys.stderr)
        return 1
    for fix in result.contrast_fixes:
        print(
            f"css-retheme: adjusted {fix.selector} text {rgb_to_hex(fix.before)} -> "
            f"{rgb_to_hex(fix.after)} ({fix.ratio_after:.1f}:1)",
            file=sys.stderr,
        )
    if args.output:
        Path(args.output).write_text(result.text, encoding="utf-8")
        print(f"Saved {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(result.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
