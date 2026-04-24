#!/usr/bin/env python3
"""CLI wrapper for openccu_data.easymodes.extractor.main."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openccu_data.easymodes.extractor import main

if __name__ == "__main__":
    sys.exit(main())
