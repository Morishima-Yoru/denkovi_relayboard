from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from typing_extensions import Self

from .structures import DiscoveredDevice


class IDenkoviRelayBoard(ABC):
    @abstractmethod
    def get_serial_number(self) -> str:
        """
        Get the serial number of the relay board.

        Returns:
            str: The serial number of the relay board.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def set_all_states_on(self) -> None:
        """
        Set all states to on.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def set_all_states_off(self) -> None:
        """
        Set all states to off.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def set_state(self, logic: bool, *addr: int) -> None:
        """
        Set the state of the relay board.

        Args:
            logic (bool): The logic of the state.
            *addr (int): The address of the relay board.

        Raises:
            RuntimeError: If the backend is not open.
            DenkoviRelayBoardStateOverflowException: If the address is out of range.
        """

    @abstractmethod
    def set_clear_state(self, logic: bool, *addr: int) -> None:
        """
        Set the clear state of the relay board.

        Args:
            logic (bool): The logic of the state.
            *addr (int): The address of the relay board.

        Raises:
            RuntimeError: If the backend is not open.
            DenkoviRelayBoardStateOverflowException: If the address is out of range.
        """

    @abstractmethod
    def get_state(self, addr: int) -> bool:
        """
        Get the state of the relay board.

        Args:
            addr (int): The address of the relay board.

        Returns:
            bool: The state of the relay board.

        Raises:
            RuntimeError: If the backend is not open.
            DenkoviRelayBoardStateOverflowException: If the address is out of range.
        """

    @abstractmethod
    def get_all_states(self) -> Tuple[bool, ...]:
        """
        Get all states of the relay board.

        Returns:
            tuple[bool, ...]: All states of the relay board.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the relay board.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def __del__(self) -> None:
        pass

    @property
    @abstractmethod
    def max_channel(self) -> int:
        """
        Get the maximum number of channels of the relay board.

        Returns:
            int: The maximum number of channels of the relay board.
        """

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()


class IBackend(ABC):
    @abstractmethod
    def open(self, device_address: Optional[str] = None, serial_number: Optional[str] = None, timeout: int = 5000) -> None:
        """
        Open the backend.

        Args:
            device_address (str | None, optional): The device address. Defaults to None.
            serial_number (str | None, optional): The serial number. Defaults to None.
            timeout (int, optional): The timeout. Defaults to 5000.

        Raises:
            ValueError: If either device_address or serial_number must be provided.
            ValueError: If both device_address and serial_number are provided.
            ValueError: If no port found for serial number.
            RuntimeError: If failed to open VCP port.
        """

    @classmethod
    @abstractmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        """
        List potential devices with the related backend.

        Returns:
            list[DiscoveredDevice]: A list of potential devices.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the backend.
        """

    @abstractmethod
    def write(self, data: bytes) -> None:
        """
        Write data to the backend.

        Args:
            data (bytes): The data to write.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from the backend.

        Args:
            size (int | None, optional): The size of the data to read. Defaults to None.

        Returns:
            bytes: The data read from the backend.

        Raises:
            RuntimeError: If the backend is not open.
        """

    @abstractmethod
    def is_open(self) -> bool:
        """
        Check if the backend is open.

        Returns:
            bool: True if the backend is open, False otherwise.
        """

    @abstractmethod
    def get_serial_number(self) -> str:
        """
        Get the serial number of the backend.

        Returns:
            str: The serial number of the backend.
        """
