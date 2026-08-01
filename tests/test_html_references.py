"""Guard: extracted display strings must be plain text, not WebUI fragments."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
import re
from typing import Any

import pytest

# A complete named or numeric character reference. Deliberately narrow so a
# bare ampersand in prose ("on/off & louder") does not register.
_REFERENCE_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,10}|#\d{1,5});")

_DATA = Path(__file__).resolve().parent.parent / "openccu_data" / "data"


def _strings(node: Any) -> list[str]:
    """Collect every string value in a decoded JSON document."""
    if isinstance(node, dict):
        return [s for v in node.values() for s in _strings(v)]
    if isinstance(node, list):
        return [s for v in node for s in _strings(v)]
    return [node] if isinstance(node, str) else []


def _load(path: Path) -> Any:
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode())


def _artefacts() -> list[Path]:
    files = sorted(_DATA.glob("*.json.gz")) + sorted(_DATA.glob("profiles/*.json.gz"))
    files += sorted(_DATA.glob("*.json")) + sorted(_DATA.glob("translation_custom/*.json"))
    return files


@pytest.mark.parametrize("path", _artefacts(), ids=lambda p: p.name)
def test_artefact_carries_no_html_references(path: Path) -> None:
    """The OCCU sources are WebUI fragments; extraction must decode them.

    A surviving "&auml;" is shown to the operator verbatim by every consumer,
    because they treat these as plain text — correctly, since escaping them
    again is what stops a device name from injecting markup.
    """
    offenders = [(s, _REFERENCE_RE.findall(s)[:3]) for s in _strings(_load(path)) if _REFERENCE_RE.search(s)]
    assert not offenders, (
        f"{path.name} carries {len(offenders)} string(s) with HTML references, "
        f"e.g. {offenders[:2]} — decode them during extraction"
    )


def test_artefact_list_is_not_empty() -> None:
    """Guard the guard: a glob that matches nothing would pass vacuously."""
    assert len(_artefacts()) > 60
