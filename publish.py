import os
import re
import subprocess
import sys


def increment_version(version_str):
    """Increments the patch version of a semver string."""
    parts = version_str.split(".")
    if len(parts) != 3:
        return version_str  # Fallback
    major, minor, patch = map(int, parts)
    return f"{major}.{minor}.{patch + 1}"


def main():
    # 1. Read current version from pyproject.toml
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    with open("pyproject.toml", "r") as f:
        content = f.read()

    match = re.search(r'version\s*=\s*"(.*?)"', content)
    if not match:
        print("Error: version not found in pyproject.toml.")
        sys.exit(1)

    old_version = match.group(1)
    new_version = increment_version(old_version)

    print(f"Current version: {old_version}")
    print(f"New version:     {new_version}")

    # 2. Update pyproject.toml
    new_content = re.sub(
        r'(version\s*=\s*")' + re.escape(old_version) + r'(")',
        f"\\1{new_version}\\2",
        content,
    )
    with open("pyproject.toml", "w") as f:
        f.write(new_content)

    # 3. Clean and Build
    print("\n--- Building package ---")
    if os.path.exists("dist"):
        subprocess.run(["rm", "-rf", "dist"], check=True)
    if os.path.exists("build"):
        subprocess.run(["rm", "-rf", "build"], check=True)

    subprocess.run([sys.executable, "-m", "build"], check=True)

    # 4. Upload
    print("\n--- Uploading to PyPI ---")
    try:
        subprocess.run([sys.executable, "-m", "twine", "upload", "dist/*"], check=True)
    except subprocess.CalledProcessError:
        print("\nError: Upload failed. Reverting version change in pyproject.toml...")
        with open("pyproject.toml", "w") as f:
            f.write(content)
        sys.exit(1)

    print(f"\nSuccessfully published version {new_version}!")


if __name__ == "__main__":
    main()
