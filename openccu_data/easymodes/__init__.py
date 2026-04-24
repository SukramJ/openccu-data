"""Easymode metadata extractor.

Parses TCL easymode configuration files from OCCU/OpenCCU/RaspberryMatic and
emits ``data/easymode_extract.json.gz``.
"""

from openccu_data.easymodes.extractor import main

__all__ = ("main",)
