from typing import List, Optional
import logging

from ..definitions.interfaces import IBackend
from ..definitions.structures import DiscoveredDevice

_logger = logging.getLogger(__name__)


class DummyBackend(IBackend):
    def __init__(self) -> None:
        pass

    def open(
        self,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        raise NotImplementedError("DummyBackend does not support this operation")

    def close(self) -> None:
        raise NotImplementedError("DummyBackend does not support this operation")

    def write(self, data: bytes) -> None:
        raise NotImplementedError("DummyBackend does not support this operation")

    def read(self, size: Optional[int] = None) -> bytes:
        raise NotImplementedError("DummyBackend does not support this operation")

    def is_open(self) -> bool:
        raise NotImplementedError("DummyBackend does not support this operation")

    def get_serial_number(self) -> str:
        raise NotImplementedError("DummyBackend does not support this operation")

    def set_bit_mode(self, mask: int, mode: int) -> None:
        raise NotImplementedError("DummyBackend does not support this operation")

    def get_bit_mode(self) -> int:
        raise NotImplementedError("DummyBackend does not support this operation")

    @classmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        return []
