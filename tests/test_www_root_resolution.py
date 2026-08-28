"""Tests for source-checkout layout detection.

Two source layouts are in use and the extractors must read both:

- OpenCCU-Base keeps the WebUI document root at ``www/``
- an OCCU tree — including the patched one the OpenCCU firmware build
  produces — keeps it at ``WebUI/www/``

Each extractor carries its own copy of ``_resolve_www_root`` (the extractors
share no helper module by design), so every copy is tested.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from openccu_data.easymodes import extractor as _EASYMODES
from openccu_data.profiles import extractor as _PROFILES
from openccu_data.translations import extractor as _TRANSLATIONS

_RESOLVERS = (
    pytest.param(_EASYMODES._resolve_www_root, id="easymodes"),
    pytest.param(_PROFILES._resolve_www_root, id="profiles"),
    pytest.param(_TRANSLATIONS._resolve_www_root, id="translations"),
)


@pytest.mark.parametrize("resolve", _RESOLVERS)
def test_openccu_base_layout(resolve, tmp_path: Path) -> None:
    """A checkout with ``www/config`` resolves to ``www``."""
    (tmp_path / "www" / "config").mkdir(parents=True)
    assert resolve(tmp_path) == tmp_path / "www"


@pytest.mark.parametrize("resolve", _RESOLVERS)
def test_occu_layout(resolve, tmp_path: Path) -> None:
    """A checkout with ``WebUI/www/config`` resolves to ``WebUI/www``."""
    (tmp_path / "WebUI" / "www" / "config").mkdir(parents=True)
    assert resolve(tmp_path) == tmp_path / "WebUI" / "www"


@pytest.mark.parametrize("resolve", _RESOLVERS)
def test_missing_config_falls_back_to_www(resolve, tmp_path: Path) -> None:
    """Without a ``config/`` directory the modern layout is reported."""
    assert resolve(tmp_path) == tmp_path / "www"


@pytest.mark.parametrize("resolve", _RESOLVERS)
def test_www_without_config_is_not_picked(resolve, tmp_path: Path) -> None:
    """An empty ``www/`` must not shadow a populated ``WebUI/www/``."""
    (tmp_path / "www").mkdir()
    (tmp_path / "WebUI" / "www" / "config").mkdir(parents=True)
    assert resolve(tmp_path) == tmp_path / "WebUI" / "www"
