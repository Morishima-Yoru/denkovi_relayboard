from contextlib import suppress
from typing import List, Optional, Set, Tuple

from ..backends import MCP2200Backend, FTD2XXBackend
from ..definitions.exceptions import DenkoviRelayBoardStateOverflowException
from ..definitions.interfaces import IDenkoviRelayBoard


class DenkoviRelayBoard4ChMCP2200(IDenkoviRelayBoard):
    READ_ALL_OPCODE = 0x80
    SET_CLEAR_OUT_OPCODE = 0x08
    IO_PORT_VAL_BMAP_IDX = 10

    def __init__(
        self,
        backend: MCP2200Backend,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        self.backend: Optional[MCP2200Backend] = None
        self.backend = backend
        self.backend.open(
            device_address=device_address,
            serial_number=serial_number,
            timeout=timeout
        )

    def get_serial_number(self) -> str:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        return self.backend.get_serial_number()

    def set_all_states_on(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(self.__construct_control_bytes([True, True, True, True]))

    def set_all_states_off(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(self.__construct_control_bytes([False, False, False, False]))

    def set_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self.__integrity_check(addr_)
        original_states: Tuple[bool, ...] = self.get_all_states()
        target_states: List[bool] = list(original_states)
        for itr in addr_:
            target_states[itr - 1] = logic
        encoded_states: bytes = self.__construct_control_bytes(target_states)
        self.backend.write(encoded_states)

    def set_clear_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self.__integrity_check(addr_)
        if not logic:
            self.set_all_states_off()
            return
        target_states: List[bool] = [(i + 1) in addr_ for i in range(4)]
        encoded_states: bytes = self.__construct_control_bytes(target_states)
        self.backend.write(encoded_states)

    def __construct_control_bytes(self, states: List[bool]) -> bytes:
        data_ = bytearray(16)
        data_[0] = self.SET_CLEAR_OUT_OPCODE
        data_[11] = sum(1 << i for i in range(4) if states[i])
        data_[12] = data_[11] ^ 0xFF
        return bytes(data_)

    def get_state(self, addr: int) -> bool:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        return self.get_all_states()[addr - 1]

    def get_all_states(self) -> Tuple[bool, ...]:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.__send_read_all_opcode()
        data_ = self.backend.read(16)
        return tuple(data_[self.IO_PORT_VAL_BMAP_IDX] & (1 << i) != 0 for i in range(4))

    def __send_read_all_opcode(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        data_ = bytearray(16)
        data_[0] = self.READ_ALL_OPCODE
        self.backend.write(bytes(data_))

    def __integrity_check(self, states: Set[int]) -> None:
        if any(state < 1 or state > 4 for state in states):
            raise DenkoviRelayBoardStateOverflowException(4)

    def close(self) -> None:
        if self.backend is not None:
            self.backend.close()
            self.backend = None

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()

    @property
    def max_channel(self) -> int:
        return 4


class DenkoviRelayBoard4ChFT422(IDenkoviRelayBoard):
    FT_SYNCHRONOUS_BIT_BANG_MODE = 0x04
    BIT_MASK = 0xFF

    def __init__(
        self,
        backend: FTD2XXBackend,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        self.backend: FTD2XXBackend = backend
        self.backend.open(
            device_address=device_address,
            serial_number=serial_number,
            timeout=timeout,
        )
        self.backend.set_bit_mode(self.BIT_MASK, self.FT_SYNCHRONOUS_BIT_BANG_MODE)

    def get_serial_number(self) -> str:
        return self.backend.get_serial_number()

    def set_all_states_on(self) -> None:
        self.backend.write(b"\xff")

    def set_all_states_off(self) -> None:
        self.backend.write(b"\x00")

    def set_state(self, logic: bool, *addr: int) -> None:
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
        return self.backend.get_bit_mode() & (1 << (addr - 1)) != 0

    def get_all_states(self) -> Tuple[bool, ...]:
        states_ = self.backend.get_bit_mode()
        return tuple(states_ & (1 << i) != 0 for i in range(8))

    def close(self) -> None:
        self.backend.close()

    def __del__(self) -> None:
        self.close()

    def __integrity_check(self, states: Set[int]) -> None:
        if any(state < 1 or state > 4 for state in states):
            raise DenkoviRelayBoardStateOverflowException(self.max_channel)

    @property
    def max_channel(self) -> int:
        return 4
