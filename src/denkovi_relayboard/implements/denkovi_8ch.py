from contextlib import suppress
from typing import List, Optional, Set, Tuple, Union
from ..definitions.exceptions import DenkoviRelayBoardStateOverflowException
from ..definitions.interfaces import IDenkoviRelayBoard
from ..backends import FTD2XXBackend, PyFtdiBackend

AcceptableBackendT = Union[FTD2XXBackend, PyFtdiBackend]


class DenkoviRelayBoard8Ch(IDenkoviRelayBoard):
    FT_SYNCHRONOUS_BIT_BANG_MODE = 0x04
    BIT_MASK = 0xFF

    def __init__(
        self,
        backend: AcceptableBackendT,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        self.backend: Optional[AcceptableBackendT] = None
        self.backend = backend
        self.backend.open(
            device_address=device_address,
            serial_number=serial_number,
            timeout=timeout,
        )
        self.backend.set_bit_mode(self.BIT_MASK, self.FT_SYNCHRONOUS_BIT_BANG_MODE)

    def get_serial_number(self) -> str:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        return self.backend.get_serial_number()

    def set_all_states_on(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(b"\xff")

    def set_all_states_off(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(b"\x00")

    def set_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self.__integrity_check(addr_)
        original_states: Tuple[bool, ...] = self.get_all_states()
        target_states: List[bool] = list(original_states)
        for itr in addr_:
            target_states[itr - 1] = logic
        encoded_states: bytes = bytes(
            [sum(1 << i for i in range(8) if target_states[i])]
        )
        self.backend.write(encoded_states)

    def set_clear_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self.__integrity_check(addr_)
        if not logic:
            self.set_all_states_off()
            return

        target_states: List[bool] = [False for _ in range(8)]
        for itr in addr_:
            target_states[itr - 1] = True
        encoded_states: bytes = bytes(
            [sum(1 << i for i in range(8) if target_states[i])]
        )
        self.backend.write(encoded_states)

    def get_state(self, addr: int) -> bool:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.__integrity_check({addr})
        return self.backend.get_bit_mode() & (1 << (addr - 1)) != 0

    def get_all_states(self) -> Tuple[bool, ...]:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        states_ = self.backend.get_bit_mode()
        return tuple(states_ & (1 << i) != 0 for i in range(8))

    def close(self) -> None:
        if self.backend is not None:
            self.backend.close()
            self.backend = None

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()

    def __integrity_check(self, states: Set[int]) -> None:
        if any(state < 1 or state > 8 for state in states):
            raise DenkoviRelayBoardStateOverflowException(self.max_channel)

    @property
    def max_channel(self) -> int:
        return 8
