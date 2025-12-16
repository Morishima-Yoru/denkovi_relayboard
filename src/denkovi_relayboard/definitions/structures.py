from typing import Optional
from typing_extensions import TypedDict, Literal

PossibleBackendT = Literal["ftd2xx", "vcp", "mcp2200", "pyftdi"]


class DiscoveredDevice(TypedDict):
    backend: PossibleBackendT
    device_address: Optional[str]
    serial_number: Optional[str]
