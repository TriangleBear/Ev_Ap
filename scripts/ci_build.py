"""CI build helper — version detection, bumping, about_view.py update, spec generation."""

import os
import re
import subprocess
import sys


def get_latest_tag() -> str:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "v0.0.0"


def parse_source_branch(merge_message: str) -> str:
    m = re.search(r"from\s+\S+/(\S+)", merge_message)
    return m.group(1) if m else "dev/unknown"


def bump_version(tag: str, branch: str) -> str:
    tag = tag.lstrip("v")
    major, minor, patch = map(int, tag.split("."))

    if re.match(r"^major/", branch):
        major += 1
        minor = 0
        patch = 0
    elif re.match(r"^(feature|feat)/", branch):
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"v{major}.{minor}.{patch}"


def update_about_view(version: str) -> None:
    path = "App/views/about_view.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r"Version:\s+(?:dev_)?\d+\.\d+\.\d+",
        f"Version: {version.lstrip('v')}",
        content,
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_spec(version: str, output_dir: str = "App/build") -> str:
    ver_dash = version.lstrip("v").replace(".", "-")
    spec_name = f"Attendance_App_{ver_dash}"
    spec_path = os.path.join(output_dir, f"{spec_name}.spec")
    os.makedirs(output_dir, exist_ok=True)

    content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{spec_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{spec_name}',
)
"""
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(content)
    return spec_name


def generate_release_notes() -> str:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "HEAD~1"],
        capture_output=True, text=True,
    )
    prev_tag = result.stdout.strip() if result.returncode == 0 else None
    if not prev_tag:
        return "Initial release."

    result = subprocess.run(
        ["git", "log", f"{prev_tag}..HEAD", "--pretty=format:- %s (%h)", "--no-merges"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.stdout.strip() else "No changes since last tag."


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-spec":
        version = sys.argv[2] if len(sys.argv) > 2 else "v0.0.0"
        spec_name = generate_spec(version)
        print(spec_name)
    else:
        merge_msg = sys.argv[1] if len(sys.argv) > 1 else "dev/ci"
        branch = parse_source_branch(merge_msg)
        latest = get_latest_tag()
        new_ver = bump_version(latest, branch)
        update_about_view(new_ver)
        notes = generate_release_notes()
        print(new_ver)
        print("---RELEASE NOTES---")
        print(notes)
