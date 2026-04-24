"""Easymode link-profile extractor.

Parses TCL easymode profile files from OCCU/OpenCCU/RaspberryMatic and emits
one JSON file per receiver channel type into ``data/profiles/``.
"""

from openccu_data.profiles.extractor import main

__all__ = ("main",)
