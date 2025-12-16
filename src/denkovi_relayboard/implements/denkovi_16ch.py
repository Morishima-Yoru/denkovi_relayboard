from contextlib import suppress
from typing import List, Optional, Set, Tuple, Union
from ..backends import FTD2XXBackend, VCPBackend, PyFtdiBackend
from ..definitions.exceptions import DenkoviRelayBoardStateOverflowException
from ..definitions.interfaces import IDenkoviRelayBoard

AcceptableBackendT = Union[FTD2XXBackend, VCPBackend, PyFtdiBackend]


class DenkoviRelayBoard16Ch(IDenkoviRelayBoard):
    """
    Denkovi 16CH implementation
    """

    EOC_PATTERN = b"//"
    EOL_PATTERN = b"\r\n"
    ASK_COMMAND = b"ask"
    POSITIVE_LOGIC_PATTERN = b"+"
    NEGATIVE_LOGIC_PATTERN = b"-"
    ON_COMMAND = b"on"
    OFF_COMMAND = b"off"
    MULTIPLE_COMMAND = b"x"

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

    def set_all_states_on(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(self.ON_COMMAND + self.EOC_PATTERN)
        self.backend.read(size=4)  # self clear buffer

    def set_all_states_off(self) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.write(self.OFF_COMMAND + self.EOC_PATTERN)
        self.backend.read(size=5)  # self clear buffer

    def set_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self._integrity_check(addr_)

        if len(addr_) == 1:
            return self._set_single_state(logic, next(iter(addr_)))

        original_states_ = list(self.get_all_states())
        for itr in addr_:
            original_states_[itr - 1] = logic
        self._set_multiple_states(original_states_)

    def set_clear_state(self, logic: bool, *addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        addr_ = set(addr)
        self._integrity_check(addr_)

        if not logic:
            self.set_all_states_off()
            return

        target_states: List[bool] = [False for _ in range(16)]
        for itr in addr_:
            target_states[itr - 1] = True
        self._set_multiple_states(target_states)

    def get_state(self, addr: int) -> bool:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self._integrity_check({addr})
        return self.get_all_states()[addr - 1]

    def get_all_states(self) -> Tuple[bool, ...]:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self.backend.read()  # self clear buffer
        self.backend.write(self.ASK_COMMAND + self.EOC_PATTERN)

        dat = self.backend.read(size=2)

        if len(dat) != 2:
            raise RuntimeError(
                f"Invalid response length: expected 2 bytes, got {len(dat)} bytes"
            )

        byte1, byte2 = dat[0], dat[1]
        states: List[bool] = []
        states.extend([bool(byte1 & (1 << bit)) for bit in range(7, -1, -1)])
        states.extend([bool(byte2 & (1 << bit)) for bit in range(7, -1, -1)])

        return tuple(states)

    def _set_multiple_states(self, states: List[bool]) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        if len(states) != 16:
            raise ValueError("The length of states must be 16.")
        byte1: int = sum((1 << i) for i in range(8) if states[7 - i])
        byte2: int = sum((1 << i) for i in range(8) if states[15 - i])
        encoded_states: bytes = bytes([byte1, byte2])
        self.backend.write(self.MULTIPLE_COMMAND + encoded_states + self.EOC_PATTERN)
        self.backend.read(size=5)  # self clear buffer

    def _set_single_state(self, logic: bool, addr: int) -> None:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        self._integrity_check({addr})
        logic_pattern = (
            self.POSITIVE_LOGIC_PATTERN if logic else self.NEGATIVE_LOGIC_PATTERN
        )
        addr_pattern = str(addr).zfill(2).encode()
        self.backend.write(addr_pattern + logic_pattern + self.EOC_PATTERN)
        self.backend.read(size=5)  # self clear buffer

    def _integrity_check(self, states: Set[int]) -> None:
        if any(state < 1 or state > 16 for state in states):
            raise DenkoviRelayBoardStateOverflowException(self.max_channel)

    def get_serial_number(self) -> str:
        if self.backend is None:
            raise RuntimeError("Backend is not open")
        return self.backend.get_serial_number()

    def close(self) -> None:
        if self.backend is not None:
            self.backend.close()
            self.backend = None

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()

    @property
    def max_channel(self) -> int:
        return 16
