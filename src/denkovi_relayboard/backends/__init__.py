"""
Communication Backends
"""
import logging

from ._dummy import DummyBackend
from .vcp_backend import VCPBackend

_logger = logging.getLogger(__name__)

# FTD2XXBackend
try:
    from .ftd2xx_backend import FTD2XXBackend  # type: ignore
except (ImportError, OSError) as e:
    _logger.warning(f"Failed to import FTD2XXBackend: {e}. Check your FTDI driver installation.")

    class FTD2XXBackend(DummyBackend):  # type: ignore
        pass

# MCP2200Backend
try:
    from .mcp2200_backend import MCP2200Backend  # type: ignore
except (ImportError, OSError) as e:
    _logger.warning(f"Failed to import MCP2200Backend: {e}")

    class MCP2200Backend(DummyBackend):  # type: ignore
        pass

# PyFtdiBackend
try:
    from .pyftdi_backend import PyFtdiBackend  # type: ignore
except (ImportError, OSError) as e:
    _logger.warning(
        f"Failed to import PyFtdiBackend: {e}. Check your pyftdi installation.\n"
        "  If need, please install it by `pip install pyftdi`."
    )

    class PyFtdiBackend(DummyBackend):  # type: ignore
        pass

__all__ = [
    "FTD2XXBackend",
    "VCPBackend",
    "MCP2200Backend",
    "PyFtdiBackend",
]
