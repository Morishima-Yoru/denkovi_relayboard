from typing_extensions import Final

MCP_VID: Final[int] = 0x04D8
MCP2200_PID: Final[int] = 0x00DF
FTDI_VID: Final[int] = 0x0403
FT232R_PID: Final[int] = 0x6001
FT232H_PID: Final[int] = 0x6014

DEFAULT_BAUD_RATE: Final[int] = 9600
DEFAULT_BYTESIZE: Final[int] = 8
DEFAULT_STOP_BITS: Final[int] = 1
DEFAULT_PARITY: Final[str] = "none"
