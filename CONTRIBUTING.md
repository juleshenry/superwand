# Contributing to superwand

## Setup

superwand uses [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/juleshenry/superwand
cd superwand
uv sync --group dev --extra studio
uvx pre-commit install   # optional: run ruff on every commit
```

## Checks

CI runs all of these on every push and pull request; run them before opening a PR.

```bash
uv run pytest --cov          # tests; coverage must stay at or above 85%
uv run ruff check .          # lint (add --fix to apply safe fixes)
uv run ruff format .         # format
uv run mypy                  # type check src/superwand
```

The Studio tests need Flask, which `--group dev` installs.

## Demo images

Every image the README shows (theme swatches, Charizards, demos, SVG examples and the gallery)
is generated, not hand-made. After changing anything that affects output, regenerate them and
commit the result:

```bash
uv run python scripts/generate_demos.py              # everything
uv run python scripts/generate_demos.py demos svg    # or just some sections
```

## Studio stylesheet

The Studio ships a prebuilt Tailwind stylesheet (`src/superwand/studio/static/studio.css`) so it
works offline. If you add or change Tailwind classes in `studio/templates/index.html`, rebuild it
(needs Node.js):

```bash
scripts/studio/build_css.sh
```

Keep new images small: `check-added-large-files` rejects files over 2 MB.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) with a scope:

```
feat(cli): add --jobs for batch runs
fix(studio): keep transparency in uploads      # bugfix(...) is also accepted
perf(regions): store a label map instead of pixel coordinates
docs(readme): document SVG retheming
chore(ci): test on Python 3.14
```

Mark breaking changes with `!` (`feat(api)!: ...`) or a `BREAKING CHANGE:` footer.
`git cliff --unreleased --strip all` (config in `cliff.toml`) turns these into draft release notes.

## Releasing

Versions come from git tags (via `hatch-vcs`), so there is no version number to edit.

1. Write the release notes under `## [Unreleased]` in `CHANGELOG.md` and merge them to `main`.
2. From an up-to-date, clean `main`, run:

   ```bash
   uv run python scripts/release.py 0.4.0 --dry-run   # check only
   uv run python scripts/release.py 0.4.0
   ```

   The script runs the tests, moves the Unreleased notes under `## v0.4.0 (date)`, commits
   `CHANGELOG.md`, tags `v0.4.0`, and asks before pushing.
3. Pushing the tag runs `.github/workflows/publish.yml`, which:
   - runs the full CI suite (lint, tests on every platform, wheel smoke test),
   - builds the sdist and wheel and checks their version matches the tag,
   - publishes to PyPI with trusted publishing (the `pypi` environment),
   - creates a GitHub release with the changelog notes and the built files attached.
