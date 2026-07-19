"""Curated device-semantics classifications.

Small, hand-maintained device classifications that downstream consumers
(aiohomematic/homematicip_local and openccu-loom) share instead of each
carrying their own hardcoded list. Data lives in
``openccu_data/data/device_semantics.json``; keys starting with ``_``
are documentation and skipped.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
import json
from typing import Final

_DATA_PACKAGE: Final = "openccu_data.data"
_FILENAME: Final = "device_semantics.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, tuple[str, ...]]:
    """Load and cache the semantics document."""
    raw = json.loads(files(_DATA_PACKAGE).joinpath(_FILENAME).read_text(encoding="utf-8"))
    return {key: tuple(value) for key, value in raw.items() if not key.startswith("_")}


def doorbell_models() -> frozenset[str]:
    """Return the device models whose press/ring channel is a doorbell.

    Consumers map the ring press of these devices onto their platform's
    doorbell semantics (e.g. Home Assistant's standard ``ring`` event
    type) instead of treating it as a generic button press.
    """
    return frozenset(_load().get("doorbell_models", ()))
