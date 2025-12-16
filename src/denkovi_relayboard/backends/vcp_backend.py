import logging
from typing import List, Optional

import serial
import serial.tools.list_ports

from ..definitions.constants import (
    DEFAULT_BAUD_RATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOP_BITS
)
from ..definitions.interfaces import IBackend
from ..definitions.structures import DiscoveredDevice

_logger = logging.getLogger(__name__)


class VCPBackend(IBackend):
    __PARITY_NAME_MAP = {
        "none": serial.PARITY_NONE,
        "even": serial.PARITY_EVEN,
        "odd": serial.PARITY_ODD,
        "mark": serial.PARITY_MARK,
        "space": serial.PARITY_SPACE,
    }

    def __init__(self,) -> None:
        self.serial_: Optional[serial.Serial] = None
        self.timeout: int = 5000
        self.serial_number: Optional[str] = None

    def open(
        self,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        """
        Open VCP backend.

        Args:
            device_address (Optional[str]): The device address.
            serial_number (Optional[str]): The serial number.
            timeout (int): The timeout.

        Raises:
            ValueError: If either device_address or serial_number must be provided.
            ValueError: If both device_address and serial_number are provided.
            ValueError: If no port found for serial number.
            RuntimeError: If failed to open VCP port.
        """
        if bool(device_address) == bool(serial_number):
            raise ValueError("Either device_address or serial_number must be provided for VCP backend")

        if device_address is None:
            assert serial_number is not None
            self.port = self.__get_port_by_serial_number(serial_number)
            if self.port is None:
                raise ValueError(f"No port found for serial number: {serial_number}")
        else:
            self.port = device_address
            serial_number = self.__get_serial_number_by_port(device_address)

        self.baudrate = DEFAULT_BAUD_RATE
        self.timeout = timeout
        self.serial_number = serial_number

        self.serial_ = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            bytesize=DEFAULT_BYTESIZE,
            parity=self.__PARITY_NAME_MAP[DEFAULT_PARITY],
            stopbits=DEFAULT_STOP_BITS,
        )

        if not self.serial_.is_open:
            raise RuntimeError(f"Failed to open VCP port {self.port}")

    def close(self) -> None:
        """
        Close VCP backend.
        """
        if self.serial_ is not None and self.serial_.is_open:
            self.serial_.close()
            self.serial_ = None

    def write(self, data: bytes) -> None:
        """
        Write data to VCP backend.

        Args:
            data (bytes): The data to write.

        Raises:
            RuntimeError: If the device is not open.
        """
        if self.serial_ is None or not self.serial_.is_open:
            raise RuntimeError("Device is not open")

        self.serial_.write(data)
        _logger.debug(f"Write {len(data)} bytes, content: {data!r}")

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from VCP backend.

        Args:
            size (Optional[int]): The size of the data to read.

        Returns:
            bytes: The data read from the VCP backend.

        Raises:
            RuntimeError: If the device is not open.
        """
        if self.serial_ is None or not self.serial_.is_open:
            raise RuntimeError("Device is not open")

        data: Optional[bytes]
        if size is not None:
            data = self.serial_.read(size)
        else:
            data = self.serial_.read_all()

        if data is None:
            data = b""

        _logger.debug(f"Read {len(data)} bytes, content: {data!r}")
        return data

    def is_open(self) -> bool:
        """
        Check if the VCP backend is open.

        Returns:
            bool: True if the VCP backend is open, False otherwise.
        """
        return self.serial_ is not None and self.serial_.is_open

    def get_serial_number(self) -> str:
        """
        Get the serial number of the VCP backend.

        Returns:
            str: The serial number of the VCP backend.

        Raises:
            RuntimeError: If the serial number is not set.
        """
        if self.serial_number is None:
            raise RuntimeError("Serial number is not set")
        return self.serial_number

    @classmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        """
        List available VCP devices.

        Returns:
            List[DiscoveredDevice]: A list of available VCP devices.
        """
        devices: List[DiscoveredDevice] = []
        for port in serial.tools.list_ports.comports():
            if port.serial_number:
                devices.append(DiscoveredDevice(
                    backend="vcp",
                    serial_number=port.serial_number,
                    device_address=port.device,
                ))
        return devices

    @staticmethod
    def __get_port_by_serial_number(serial_number: str) -> Optional[str]:
        for port in serial.tools.list_ports.comports():
            if port.serial_number is None:
                continue
            if serial_number.lower() in port.serial_number.lower():
                return port.device
        return None

    @staticmethod
    def __get_serial_number_by_port(device_address: str) -> Optional[str]:
        for port in serial.tools.list_ports.comports():
            if port.device == device_address:
                return port.serial_number
        return None
