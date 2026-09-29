"""Tests for the device image extractor and the committed image tree."""

from __future__ import annotations

from pathlib import Path

from openccu_data.device_images import extractor as _EXTRACTOR

_DATA_DIR = Path(_EXTRACTOR._DEFAULT_OUTPUT_DIR)
_IMAGE_DIR = _DATA_DIR / _EXTRACTOR._OUTPUT_SUBDIR

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_copy_images_is_byte_identical_and_keeps_subdirectories(tmp_path: Path) -> None:
    """Every PNG is copied unchanged, subdirectories survive, other files are skipped."""
    src = tmp_path / "src"
    (src / "coupling").mkdir(parents=True)
    (src / "a.png").write_bytes(_PNG_MAGIC + b"a")
    (src / "coupling" / "b.png").write_bytes(_PNG_MAGIC + b"b")
    (src / "readme.txt").write_text("not an image")
    dst = tmp_path / "dst"
    (dst / "stale.png").parent.mkdir(parents=True)
    (dst / "stale.png").write_bytes(b"old")

    copied = _EXTRACTOR.copy_images(src, dst)

    assert copied == ["a.png", "coupling/b.png"]
    assert (dst / "a.png").read_bytes() == _PNG_MAGIC + b"a"
    assert (dst / "coupling" / "b.png").read_bytes() == _PNG_MAGIC + b"b"
    assert not (dst / "readme.txt").exists()
    assert not (dst / "stale.png").exists()


def test_missing_images_lists_every_referencing_model() -> None:
    """A missing filename is reported with all models that reference it."""
    icons = {"M1": "x.png", "M2": "x.png", "M3": "coupling/y.png", "M4": "z.png"}
    missing = _EXTRACTOR.missing_images(icons, {"z.png"})
    assert missing == {"x.png": ["M1", "M2"], "coupling/y.png": ["M3"]}


def test_committed_tree_covers_every_device_icon() -> None:
    """Every filename in the committed device_icons table exists as a PNG in the committed tree."""
    icons = _EXTRACTOR.load_device_icons(_DATA_DIR / _EXTRACTOR._TRANSLATION_ARCHIVE)
    assert icons, "device_icons table is empty"
    available = {p.relative_to(_IMAGE_DIR).as_posix() for p in _IMAGE_DIR.rglob("*.png")}
    assert _EXTRACTOR.missing_images(icons, available) == {}
    assert any(name.startswith("coupling/") for name in icons.values())
    for name in set(icons.values()):
        assert (_IMAGE_DIR / name).read_bytes()[:8] == _PNG_MAGIC, name
