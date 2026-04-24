"""CCU WebUI translation extractor.

Parses JavaScript translation files plus the stringtable mapping from the CCU
WebUI and emits ``data/translation_extract.json.gz``.
"""

from openccu_data.translations.extractor import main

__all__ = ("main",)
