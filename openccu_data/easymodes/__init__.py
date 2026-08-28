"""Easymode metadata extractor.

Parses TCL easymode configuration files from OpenCCU-Base/OpenCCU and
emits ``data/easymode_extract.json.gz``.
"""

from openccu_data.easymodes.extractor import main

__all__ = ("main",)
