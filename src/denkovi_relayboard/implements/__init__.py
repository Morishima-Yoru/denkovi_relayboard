"""
Denkovi Relay Board Implements
"""

from .denkovi_16ch import DenkoviRelayBoard16Ch
from .denkovi_8ch import DenkoviRelayBoard8Ch
from .denkovi_4ch import DenkoviRelayBoard4ChFT422, DenkoviRelayBoard4ChMCP2200

__all__ = [
    "DenkoviRelayBoard16Ch",
    "DenkoviRelayBoard8Ch",
    "DenkoviRelayBoard4ChFT422",
    "DenkoviRelayBoard4ChMCP2200",
]
