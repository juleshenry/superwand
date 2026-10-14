"""
Cuts a release: stamps CHANGELOG.md, commits it, tags, and pushes. Pushing the
tag runs .github/workflows/publish.yml, which tests, builds and publishes to PyPI.

    uv run python scripts/release.py 0.4.0
    uv run python scripts/release.py 0.4.0 --dry-run

Before running it, write the release notes under `## [Unreleased]` in
CHANGELOG.md (`git cliff --unreleased` drafts them from commit messages).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
UNRELEASED = "## [Unreleased]"
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

Version = tuple[int, int, int]


def die(message: str) -> NoReturn:
    print(f"release: error: {message}", file=sys.stderr)
    sys.exit(1)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        die(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def parse_version(text: str) -> Version | None:
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def latest_released() -> Version | None:
    """Highest vX.Y.Z tag; tags that aren't X.Y.Z (like the stray `v20`) are ignored."""
    versions = [v for tag in git("tag", "--list", "v*").split() if (v := parse_version(tag))]
    return max(versions, default=None)


def split_changelog(text: str) -> tuple[str, str, str]:
    """Returns (before, unreleased notes, rest) around the Unreleased section."""
    start = text.find(UNRELEASED)
    if start == -1:
        die(f"CHANGELOG.md has no '{UNRELEASED}' section")
    body_start = start + len(UNRELEASED)
    nxt = text.find("\n## ", body_start)
    end = len(text) if nxt == -1 else nxt + 1
    return text[:start], text[body_start:end], text[end:]


def check_repo(tag: str) -> None:
    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        die("releases are cut from main; check out main first")
    if git("status", "--porcelain"):
        die("the working tree has uncommitted changes; commit or stash them first")
    git("fetch", "--quiet", "--tags", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        die("main is not in sync with origin/main; pull or push first")
    if git("tag", "--list", tag):
        die(f"tag {tag} already exists")


def run_tests() -> None:
    print("Running the test suite...")
    if subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT).returncode != 0:
        die("tests failed; not releasing")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tag and publish a superwand release.")
    parser.add_argument("version", help="New version, X.Y.Z (e.g. 0.4.0)")
    parser.add_argument("--dry-run", action="store_true", help="Check everything, change nothing.")
    parser.add_argument("--skip-tests", action="store_true", help="Don't run pytest first.")
    args = parser.parse_args()

    new = parse_version(args.version)
    if new is None:
        die(f"version must look like X.Y.Z, got {args.version!r}")
    version = ".".join(map(str, new))
    tag = f"v{version}"

    latest = latest_released()
    if latest is not None and new <= latest:
        die(f"{tag} is not newer than the latest release v{'.'.join(map(str, latest))}")

    check_repo(tag)

    before, notes, rest = split_changelog(CHANGELOG.read_text(encoding="utf-8"))
    notes = COMMENT_RE.sub("", notes).strip()
    if not notes:
        die(
            f"the '{UNRELEASED}' section of CHANGELOG.md is empty. Write the release notes "
            "first; `git cliff --unreleased --strip all` drafts them from commit messages."
        )

    if not args.skip_tests:
        run_tests()

    today = dt.date.today().isoformat()
    stamped = f"{before}{UNRELEASED}\n\n## {tag} ({today})\n\n{notes}\n\n{rest}"

    print(f"\nRelease {tag} ({today}) with these notes:\n\n{notes}\n")
    if args.dry_run:
        print("Dry run: CHANGELOG.md, commits and tags are untouched.")
        return

    CHANGELOG.write_text(stamped, encoding="utf-8")
    git("add", "CHANGELOG.md")
    git("commit", "--quiet", "-m", f"chore(release): {tag}")
    git("tag", "--annotate", tag, "-m", f"superwand {tag}")
    print(f"Committed CHANGELOG.md and tagged {tag}:")
    print(git("log", "--oneline", "-1"))

    answer = input(f"\nPush main and {tag} to origin (this publishes to PyPI)? [y/N] ")
    if answer.strip().lower() not in ("y", "yes"):
        print(
            "\nNot pushed. To publish later:   git push --atomic origin main "
            f"{tag}\nTo undo locally:                git tag -d {tag} && git reset --hard HEAD~1"
        )
        return
    git("push", "--atomic", "origin", "main", tag)
    print("Pushed. Follow the release at https://github.com/juleshenry/superwand/actions")


if __name__ == "__main__":
    main()
