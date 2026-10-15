#!/usr/bin/python3
"""Verify the real App bundle, manifest, architecture and Mach-O deployment target."""

import argparse
import json
from pathlib import Path
import plistlib
import re
import subprocess


def version(value):
    parts = tuple(int(part) for part in value.split("."))
    if not 1 <= len(parts) <= 3 or any(part < 0 for part in parts):
        raise ValueError("Invalid version: " + value)
    return parts + (0,) * (3 - len(parts))


def validate_metadata(info, manifest, architectures, build_info):
    required = version("26.2")
    platforms = [item for item in manifest["platforms"] if item["platformName"] == "macos"]
    if len(platforms) != 1 or version(platforms[0]["version"]) != required:
        raise ValueError("Package.swift must declare macOS 26.2.")
    if version(info["LSMinimumSystemVersion"]) != required:
        raise ValueError("Info.plist must declare macOS 26.2.")
    if info["CFBundleExecutable"] != "UniversalAIStudio" or info["CFBundlePackageType"] != "APPL":
        raise ValueError("Unexpected App bundle identity.")
    if architectures.split() != ["arm64"]:
        raise ValueError("The App must contain only arm64.")
    minimums = re.findall(r"^\s*minos\s+(\S+)", build_info, re.MULTILINE)
    if len(minimums) != 1 or version(minimums[0]) != required:
        raise ValueError("Mach-O LC_BUILD_VERSION must declare minos 26.2.")
    if not re.search(r"^\s*platform\s+MACOS\s*$", build_info, re.MULTILINE):
        raise ValueError("Mach-O must target macOS.")


def verify(app):
    root = Path(__file__).resolve().parents[1]
    with (app / "Contents/Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    executable = app / "Contents/MacOS/UniversalAIStudio"
    if not executable.is_file() or not executable.stat().st_mode & 0o111:
        raise ValueError("App executable is missing or not executable.")
    manifest = json.loads(subprocess.check_output(["swift", "package", "dump-package"], cwd=root))
    architectures = subprocess.check_output(["/usr/bin/lipo", "-archs", str(executable)], text=True).strip()
    build_info = subprocess.check_output(["xcrun", "vtool", "-show-build", str(executable)], text=True)
    validate_metadata(info, manifest, architectures, build_info)
    subprocess.run(["/usr/bin/codesign", "--verify", "--strict", str(app)], check=True)
    return {"app": str(app), "architecture": architectures, "minimum_macos": "26.2", "mach_o": build_info, "status": "passed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.app), indent=2))
