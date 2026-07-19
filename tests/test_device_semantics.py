"""Tests for the curated device-semantics classifications."""

from __future__ import annotations

from openccu_data.device_semantics import doorbell_models


def test_doorbell_models_contains_curated_devices() -> None:
    """The three curated doorbell devices are classified."""
    models = doorbell_models()
    assert isinstance(models, frozenset)
    assert {"HM-Sen-DB-PCB", "HmIP-DBB", "HmIP-DSD-PCB"} <= models


def test_doorbell_models_carries_no_documentation_keys() -> None:
    """Underscore-prefixed documentation keys never leak into results."""
    assert all(not model.startswith("_") for model in doorbell_models())
