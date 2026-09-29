#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2021-2026
"""
Copy the CCU WebUI device images into the data tree.

The CCU WebUI renders every device with a PNG from
``config/img/devices/250/`` below the WebUI document root (the 250 px
variant). The filename per device model is recorded in the ``device_icons``
table of ``translation_extract.json.gz`` (parsed from ``DEVDB.tcl``). This extractor
copies those images byte-for-byte to ``data/device_images/250/`` so consumers
without a WebUI (for example a CCU replacement that serves no ``/config/img``)
can still show them. Subdirectories are kept: eleven ``device_icons`` entries
point at ``coupling/<name>.png``.

After copying, every filename referenced by ``device_icons`` must exist in the
output tree. A missing file is listed and the run fails with a non-zero exit
code; nothing is guessed or filtered away.

Usage:
    OPENCCUBASE_PATH=/path/to/OpenCCU-Base openccu-extract-device-images

    # Custom output directory
    OPENCCUBASE_PATH=/path/to/OpenCCU-Base OUTPUT_DIR=custom/path openccu-extract-device-images

Environment Variables:
    OPENCCUBASE_PATH  Path to local OpenCCU-Base checkout (required)
    OUTPUT_DIR        Output directory (default: openccu_data/data)
"""

from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
import shutil
import sys

# Image directory below the WebUI document root. Only the 250 px variant is
# extracted; the WebUI's device views use it as well.
_IMAGE_SUBDIR = "config/img/devices/250"

# Output directory below OUTPUT_DIR; keeps the size variant in the path so a
# later variant can be added without renaming.
_OUTPUT_SUBDIR = "device_images/250"

# Archive carrying the device model -> image filename table.
_TRANSLATION_ARCHIVE = "translation_extract.json.gz"
_DEVICE_ICONS_KEY = "device_icons"

# Default output directory (relative to project root)
_DEFAULT_OUTPUT_DIR = str(Path(__file__).resolve().parent.parent / "data")


def _load_dotenv(env_file: Path) -> None:
    """Load environment variables from a .env file (stdlib-only, no python-dotenv needed)."""
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def _resolve_www_root(base_path: Path) -> Path:
    """
    Return the WebUI document root inside a source checkout.

    Two layouts are in use: OpenCCU-Base keeps the document root at ``www/``,
    while an OCCU tree — including the patched one the OpenCCU firmware build
    produces — keeps it at ``WebUI/www/``. Pick whichever actually carries the
    ``config/`` directory the extractors read; fall back to ``www/`` so the
    caller reports a missing path against the modern layout.
    """
    for candidate in (base_path / "www", base_path / "WebUI" / "www"):
        if (candidate / "config").is_dir():
            return candidate
    return base_path / "www"


def copy_images(source_dir: Path, target_dir: Path) -> list[str]:
    """
    Copy every ``*.png`` below ``source_dir`` to ``target_dir``, byte-identical.

    The target is cleared first so an image removed upstream does not linger.
    Return the copied paths relative to ``target_dir`` (POSIX separators, sorted).
    """
    if target_dir.exists():
        shutil.rmtree(target_dir)
    copied: list[str] = []
    for src in sorted(source_dir.rglob("*.png")):
        if not src.is_file():
            continue
        rel = src.relative_to(source_dir)
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        # copyfile copies content only; no metadata, so the committed tree
        # does not depend on the checkout's timestamps or modes.
        shutil.copyfile(src, dst)
        copied.append(rel.as_posix())
    return copied


def load_device_icons(archive_path: Path) -> dict[str, str]:
    """Return the ``device_icons`` table (device model -> image filename) from the archive."""
    with gzip.open(archive_path, "rb") as fh:
        archive = json.loads(fh.read().decode("utf-8"))
    icons = archive.get(_DEVICE_ICONS_KEY)
    if not isinstance(icons, dict):
        raise ValueError(f"{archive_path}: no '{_DEVICE_ICONS_KEY}' table")
    return {str(model): str(filename) for model, filename in icons.items()}


def missing_images(device_icons: dict[str, str], available: set[str]) -> dict[str, list[str]]:
    """Return referenced filenames absent from ``available``, each with the models that reference it."""
    missing: dict[str, list[str]] = {}
    for model, filename in sorted(device_icons.items()):
        if filename not in available:
            missing.setdefault(filename, []).append(model)
    return missing


def main() -> int:
    """Run the extraction."""
    project_root = Path(__file__).resolve().parent.parent.parent
    _load_dotenv(project_root / ".env")

    openccubase_path = os.environ.get("OPENCCUBASE_PATH")
    output_dir_str = os.environ.get("OUTPUT_DIR", _DEFAULT_OUTPUT_DIR)

    if not openccubase_path:
        print("ERROR: Set OPENCCUBASE_PATH (local OpenCCU-Base checkout).", file=sys.stderr)
        return 1

    base = Path(openccubase_path)
    if not base.is_absolute():
        base = project_root / base
    source_dir = _resolve_www_root(base.resolve()) / _IMAGE_SUBDIR
    if not source_dir.is_dir():
        print(f"ERROR: image directory not found: {source_dir}", file=sys.stderr)
        return 1

    output_dir = Path(output_dir_str)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir
    target_dir = output_dir / _OUTPUT_SUBDIR

    print(f"Copying device images from {source_dir} ...")
    copied = copy_images(source_dir, target_dir)
    total_bytes = sum((target_dir / rel).stat().st_size for rel in copied)
    print(f"  {len(copied)} images, {total_bytes / 1024:.0f} KB -> {target_dir}")

    archive_path = output_dir / _TRANSLATION_ARCHIVE
    if not archive_path.is_file():
        print(f"ERROR: {archive_path} not found; run the translation extractor first.", file=sys.stderr)
        return 1
    device_icons = load_device_icons(archive_path)
    missing = missing_images(device_icons, set(copied))
    if missing:
        print(
            f"ERROR: {len(missing)} image(s) referenced by {_DEVICE_ICONS_KEY} are missing:",
            file=sys.stderr,
        )
        for filename, models in missing.items():
            print(f"  {filename}  (models: {', '.join(models)})", file=sys.stderr)
        return 1

    referenced = len(set(device_icons.values()))
    print(f"  all {referenced} images referenced by {len(device_icons)} {_DEVICE_ICONS_KEY} entries present")
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
