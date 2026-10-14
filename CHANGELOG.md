# Changelog

All notable changes to superwand are recorded here. Versions follow
[Semantic Versioning](https://semver.org/); while the major version is 0, minor
releases may contain breaking changes, and those are called out explicitly.

## [Unreleased]

### Breaking changes

* `pip install superwand` no longer installs Flask. Install `superwand[studio]` for SuperWand Studio; `superwand` with no inputs explains this when Flask is missing.
* `superwand image.png` with no theme now writes every theme (what `--headless` used to do) instead of launching the Studio. Run `superwand` with no inputs for the Studio.
* Regions are found in the OKLab color space and gradients blend in OKLab, so outputs differ slightly from 0.3. `space="rgb"` / `--space rgb` restores RGB clustering.
* Modules moved: `superwand.core.*` and `superwand.utils.*` are gone in favor of `superwand.regions`, `render`, `themes`, `gradients`, `css`, `svg`, `gif`, `color`, `palette_io` and `cli`. Everything in `superwand.__all__` is importable from the top level.
* `extract_palette(image, number=...)` is now `extract_palette(image, k=...)`.
* `css_retheme()` raises `ValueError` for an unknown theme instead of silently using Tropical, and no longer recolors colors inside quoted strings or `url()`.
* `gradient_enforce()` keeps transparency, so it returns RGBA for transparent inputs (RGB otherwise).

### Added

* Transparency is preserved everywhere: transparent pixels are ignored when finding regions and keep their alpha in every output, including GIFs.
* `--preserve-shading` / `shading=True` keeps each pixel's lightness relative to its region, so photos keep their texture.
* `--smooth` / `smooth=True` blends anti-aliased edges between the two nearest regions.
* SVG retheming (`svg_retheme()`, or pass `.svg` files to `superwand` or `css-retheme`): `fill`, `stroke`, `stop-color`, `flood-color`, `lighting-color`, `color`, `style` attributes and `<style>` blocks.
* CSS: `hsl()`/`hsla()`, `oklch()`, `oklab()`, percentage and space-separated `rgb()`, and named colors in color properties; the original notation, case and alpha are kept.
* CSS contrast repair: `--min-contrast 4.5` / `min_contrast=` lightens or darkens text colors that would fall below a WCAG ratio against their rule's background; `css-retheme --check` lists low-contrast pairs.
* Themes from anywhere: color lists (`-t "#ff0080,#00ffff"`), palette files (`.json`, `.toml`, `.gpl`, `.ase`, `.hex`/`.txt`, `.css` variables), and a user themes folder (`~/.config/superwand/themes` or `$SUPERWAND_THEMES_DIR`). Theme names are case- and accent-insensitive (`paixao`).
* Palette export: `--palette FILE` and `--format hex|json|css|gpl|ase`, plus `load_palette()` / `save_palette()`.
* Region control: `--lock N` keeps region N's original pixels and `--map N=COLOR` pins it; `overrides=` in `retheme()`. `--palette` now prints numbered regions with their share of the image.
* Batch runs: several inputs, folders and globs in one command, `-j/--jobs` for parallel processing, and repeatable `-t`.
* New API: `find_regions()` returning a `Regions` object (label map, colors, counts) that can be reused across calls, `paint()`, `retheme_file()`, `parse_color()`, `parse_palette()`, `all_themes()`, `themes_dir()`.
* `python -m superwand`, `superwand --version`, `--host` for the Studio, `-q/--quiet`, `--delay` for GIFs.
* Studio: smooth-edges and preserve-shading toggles, a before/after compare slider, region shares, SVG upload with rendered previews, CSS match mode and contrast repair, and an upload store capped by item count and memory. Regions are cached per image and `k`.
* Type hints throughout, shipped with `py.typed`.

### Changed

* Region data is stored as one label map instead of per-region pixel coordinate lists: about 30% less peak memory on a 24-megapixel image (0.94 GB to 0.67 GB), and every rendering mode works in bounded row bands.
* CLI flags use double dashes (`--theme`, `--gradient`, `--palette-from`, ...); the old single-dash spellings still work and are hidden from `--help`.
* Errors go to stderr with a non-zero exit code (2 for usage errors, 1 when an input fails). Other inputs in a batch still run.
* The Studio serves a locally built stylesheet instead of the Tailwind CDN, so it works offline. It no longer configures global logging when imported.
* Versions come from git tags; releases go through `scripts/release.py` and a CI-gated publish workflow.

### Fixed

* Transparent backgrounds were rethemed along with the subject.
* `gradient-enforce` exited with status 0 after errors.
* Fewer distinct colors than `k` no longer triggers scikit-learn convergence warnings.
* The Studio region arrow icon had an invalid SVG path.

### Deprecated

* `SuperWand`, `np_get_prominent_regions()` and `np_inject_theme()` still work but warn; they will be removed in 0.5. Use `retheme()`, `find_regions()` and `retheme_file()`.
* `-tolerance`, and `gradient-enforce --completeness` / `--opacity`, never had an effect; they now warn and will be removed in 0.5.

### Removed

* The bundled Arial Unicode font (a proprietary font, 23 MB of the 15.6 MB wheel); labels use Pillow's built-in font. The wheel is now about 70 KB.
* Unused and scratch modules: the pure-Python region finder, the interactive prompt helpers, and `np_colorgram`.
* Dependencies `matplotlib` (never imported) and `pillow-avif-plugin` (Pillow 11.3+ reads AVIF natively).
* Test images and theme swatches from the installed package.

## v0.3.1 – v0.3.3 (2026-09-30)

* Stop tracking build artifacts (`dist/`, `*.egg-info`) in git. No changes to the library itself.

## v0.3.0 (2026-09-30)

* Add `retheme()`, `transfer_palette()` and `extract_palette()` Python API returning PIL Images.
* Add `-palette-from` (palette transfer from a reference image) and `-match order|luminance`.
* Add `-gif` / `theme_cycle_gif()` for an animated, labeled theme cycle.
* Add `-palette`, `-o/--output-dir`, `--list-themes`, `--port`, `--debug` CLI flags; theme runs print saved paths.
* Add `css-retheme` CLI. CSS rethemer now handles `#rgb`/`#rgba`/`#rrggbbaa`/`rgb()`/`rgba()`, preserves alpha, indentation, selectors and comments, and replaces every color on a line (previously only the first).
* Vectorize `gradient_enforce` (25-33x faster, pixel-identical output) and deduplicate gradient math.
* Seed region sampling so results are reproducible; fill themes shorter than `k` by cycling instead of random picks.
* Studio no longer runs in Flask debug mode by default.
* Fix `gif_maker.inv` inverting columns instead of color channels.
* Remove debug prints; require Python >= 3.10 (code uses `match`); test on 3.13.
* Add demos in `examples/demos/` generated by `scripts/generate_demos.py`.

## v0.2.0 – v0.2.10 (2026-02-27)

* Studio: accept AVIF uploads via `pillow-avif-plugin`, including AVIF files saved with a `.jpg` extension.
* Studio: normalize every uploaded image to PNG and serve it from a new `/image/<name>` route, so the browser preview works for any format Pillow can read.
* Studio: return a clear error for unreadable images instead of a server error, and raise the upload limit from 16 MB to 32 MB.

## v0.1.11 – v0.1.19 (2026-02-14 – 2026-02-27)

* Studio: keep uploads in memory instead of writing to the package directory, which failed when superwand was installed with pip.
* Fix PyPI trusted publishing ("invalid-publisher") and release versioning. The stray `v20` tag from this period is not a real release.
* README and release-script fixes; tests write to temporary directories instead of the working tree.

## v0.1.10 (2026-02-14)

* Update README image links to use blob ?raw=1 style for better PyPI compatibility.
* Replace 'intensity' with 'polarity' in core retheming logic and Studio UI.
* Make gradient instructions more explicit in CLI and README.
* Add support for explicit start and end colors in `gradient-enforce`.

## v0.1.1 – v0.1.9 (2026-02-14)

* Packaging, README and release-script fixes following the first release.

## v0.1.0 (2026-02-14)

* Initial release of superwand.
* A tool for retheming images and CSS using color palettes and gradients.
