import os
import subprocess
import sys
import re
from datetime import datetime


def run_command(command, error_msg=None):
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=False, text=True)
    if process.returncode != 0:
        if error_msg:
            print(f"ERROR: {error_msg}")
        else:
            print(f"\nCommand failed with exit code {process.returncode}")
        sys.exit(1)


def update_file(file_path, old_pattern, new_text):
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        content = f.read()

    new_content = re.sub(old_pattern, new_text, content)

    with open(file_path, "w") as f:
        f.write(new_content)


def update_changelog(new_version):
    file_path = "CHANGELOG.md"
    if not os.path.exists(file_path):
        return

    # Ensure version doesn't have double 'v'
    display_version = new_version if new_version.startswith("v") else f"v{new_version}"

    date_str = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"\n## {display_version} ({date_str})\n\n* Automated release update\n"

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Insert after the header
    inserted = False
    for i, line in enumerate(lines):
        if line.startswith("# Changelog"):
            lines.insert(i + 1, new_entry)
            inserted = True
            break

    if not inserted:
        lines.insert(0, f"# Changelog\n{new_entry}")

    with open(file_path, "w") as f:
        f.writelines(lines)


def get_current_version():
    if not os.path.exists("pyproject.toml"):
        return "0.0.0"
    with open("pyproject.toml", "r") as f:
        content = f.read()
    match = re.search(r'version = "(.*)"', content)
    return match.group(1) if match else "0.0.0"


def main():
    current_version = get_current_version()

    if len(sys.argv) < 2:
        print(f"Current local version (pyproject.toml): {current_version}")

        # Smart version increment suggestion
        parts = current_version.split(".")
        if len(parts) == 3 and parts[2].isdigit():
            suggested = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        else:
            suggested = current_version + ".1"

        new_version = input(f"Enter new version [default: {suggested}]: ").strip()
        if not new_version:
            new_version = suggested
    else:
        new_version = sys.argv[1]

    print(f"--- Preparing Distribution for v{new_version} ---")

    # 1. Update version files
    print(f"Updating pyproject.toml to v{new_version}...")
    update_file("pyproject.toml", r'version = ".*"', f'version = "{new_version}"')

    print(f"Updating src/superwand/__init__.py to v{new_version}...")
    update_file(
        "src/superwand/__init__.py",
        r'__version__ = ".*"',
        f'__version__ = "{new_version}"',
    )

    # 2. Update CHANGELOG.md
    print("Updating CHANGELOG.md...")
    update_changelog(new_version)

    # 3. Clean and Build
    print("Cleaning old builds...")
    if os.path.exists("dist"):
        run_command("rm -rf dist/*")
    if os.path.exists("src/superwand.egg-info"):
        run_command("rm -rf src/superwand.egg-info")

    print("Building package...")
    run_command(
        "python3 -m build", "Build failed. Check your pyproject.toml and dependencies."
    )

    # 4. Git Operations
    print("Committing and tagging in git...")
    tag_version = new_version if new_version.startswith("v") else f"v{new_version}"
    run_command(f"git add pyproject.toml src/superwand/__init__.py CHANGELOG.md")
    # Check if there are changes to commit
    status = subprocess.run("git diff --cached --quiet", shell=True).returncode
    if status != 0:
        run_command(f'git commit -m "Release {tag_version}"')

    # Check if tag already exists
    tag_exists = (
        subprocess.run(
            f"git rev-parse {tag_version}", shell=True, capture_output=True
        ).returncode
        == 0
    )
    if tag_exists:
        print(f"Tag {tag_version} already exists. Skipping tagging.")
    else:
        run_command(f"git tag {tag_version}")

    # 5. Push to git to trigger CI/CD
    print("\nPushing to git to trigger CI/CD...")
    run_command(f"git push origin main")
    run_command(f"git push origin --tags")
    print("\nDone! Push complete. GitHub Actions should handle the publication.")

    print(f"\nSuccessfully processed {tag_version}.")


if __name__ == "__main__":
    main()
