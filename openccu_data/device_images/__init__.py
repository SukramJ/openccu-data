"""CCU WebUI device image extractor.

Copies the 250 px device images from an OpenCCU-Base checkout into
``data/device_images/250/`` and checks them against ``device_icons``.
"""

from openccu_data.device_images.extractor import main

__all__ = ("main",)
