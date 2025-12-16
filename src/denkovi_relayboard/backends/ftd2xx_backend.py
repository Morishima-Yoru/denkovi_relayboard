from typing import List, Optional
import logging
import serial.tools.list_ports

from ..definitions.interfaces import IBackend
from ..definitions.constants import (
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOP_BITS
)
from ..ftd2xx_python.core import PyFTD2XXWrapper
from ..ftd2xx_python.definitions.namespace import (
    FTParity,
    FTBaudRates,
    FTStopBits,
)
from ..definitions.structures import DiscoveredDevice

_logger = logging.getLogger(__name__)


class FTD2XXBackend(IBackend):
    __PARITY_NAME_MAP = {
        "none": FTParity.NONE,
        "even": FTParity.EVEN,
        "odd": FTParity.ODD,
        "mark": FTParity.MARK,
        "space": FTParity.SPACE,
    }
    __STOP_BITS_NAME_MAP = {1: FTStopBits.STOP_BITS_1, 2: FTStopBits.STOP_BITS_2}

    def __init__(self) -> None:
        self.wrapper: PyFTD2XXWrapper = PyFTD2XXWrapper()
        self.serial_number: Optional[str] = None
        self.port: Optional[str] = None
        self.timeout: int = 5000

    def open(
        self,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5,
    ) -> None:
        """
        Open FTD2XX backend.

        Args:
            device_address (Optional[str]): The device address.
            serial_number (Optional[str]): The serial number.
            timeout (int): The timeout.

        Raises:
            ValueError: If the device_address and serial_number are both provided.
            ValueError: If the device_address and serial_number are both not provided.
            ValueError: If the serial_number is not found.
        """
        if bool(device_address) == bool(serial_number):
            raise ValueError("Either device_address or serial_number must be provided for FTD2XX backend")

        if device_address is None:
            assert serial_number is not None
            self.serial_number = self.__get_actual_serial_number(serial_number)
            if self.serial_number is None:
                raise ValueError(f"No FTDI device found with serial number {serial_number}")
            self.port = self.__get_port_by_serial_number(self.serial_number)
        else:
            self.port = device_address
            self.serial_number = self.__get_serial_number_by_port(self.port)
            if self.serial_number is None:
                raise ValueError(f"No FTDI device found with port {device_address}")

        self.timeout = timeout
        self._open_by_serial_number(self.serial_number)
        self.wrapper.ft_set_baudrate(FTBaudRates.BAUD_9600)
        self.wrapper.set_data_characteristics(
            bits=DEFAULT_BYTESIZE,
            stop_bits=self.__STOP_BITS_NAME_MAP[DEFAULT_STOP_BITS],
            parity=self.__PARITY_NAME_MAP[DEFAULT_PARITY],
        )
        self.wrapper.set_timeout(self.timeout, self.timeout)

    def close(self) -> None:
        """
        Close FTD2XX backend.
        """
        self.wrapper.ft_close()

    def write(self, data: bytes) -> None:
        """
        Write data to FTD2XX backend.

        Args:
            data (bytes): The data to write.

        Raises:
            FTD2XXException: If failed to write.
        """
        self.wrapper.write(data)
        _logger.debug(f"Write {len(data)} bytes, content: {data!r}")

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from FTD2XX backend.

        Args:
            size (Optional[int]): The size of the data to read.

        Returns:
            bytes: The data read from the FTD2XX backend.

        Raises:
            FTD2XXException: If failed to read.
        """
        data = self.wrapper.read(size=size)
        _logger.debug(f"Read {len(data)} bytes, content: {data!r}")
        return data

    def is_open(self) -> bool:
        """
        Check if the FTD2XX backend is open.

        Returns:
            bool: True if the FTD2XX backend is open, False otherwise.
        """
        return self.wrapper.is_open()

    def get_serial_number(self) -> str:
        """
        Get the serial number of the FTD2XX backend.

        Returns:
            str: The serial number of the FTD2XX backend.
        """
        return self.serial_number or ""

    def set_bit_mode(self, mask: int, mode: int) -> None:
        """
        Set the bit mode of the FTD2XX backend.

        Args:
            mask (int): The mask.
            mode (int): The mode.

        Raises:
            FTD2XXException: If failed to set bit mode.
        """
        self.wrapper.set_bit_mode(mask, mode)
        _logger.debug(f"Set bit mode: {mask}, {mode}")

    def get_bit_mode(self) -> int:
        """
        Get the bit mode of the FTD2XX backend.

        Returns:
            int: The GPIO bit status.

        Raises:
            FTD2XXException: If failed to get bit mode.
        """
        ret_ = self.wrapper.get_bit_mode()
        _logger.debug(f"Get bit mode: {ret_}")
        return ret_

    @classmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        """
        List available FTD2XX devices.

        Returns:
            List[DiscoveredDevice]: A list of available FTD2XX devices.
        """
        devices: List[DiscoveredDevice] = []
        try:
            wrapper = PyFTD2XXWrapper()
            info_list = wrapper.get_devices_info()
            for info in info_list:
                if info.id == 0 and info.loc_id == 0:
                    # Skip the sio conflict device
                    continue
                devices.append(DiscoveredDevice(
                    backend="ftd2xx",
                    serial_number=info.serial_number,
                    device_address=cls.__get_port_by_serial_number(info.serial_number),
                ))
        except Exception as e:
            _logger.warning(f"Failed to list FTD2XX devices: {e}")
        return devices

    def _open_by_serial_number(self, serial_number: str) -> None:
        self.wrapper.ft_open_by_serial_number(serial_number)

    def _open_by_port(self, port: str) -> None:
        ftdi_devices = self.wrapper.get_devices_info()
        com_ports = serial.tools.list_ports.comports()
        target_port_info = None
        for port_info in com_ports:
            if port_info.device == port:
                target_port_info = port_info
                break

        if target_port_info is None or target_port_info.serial_number is None:
            raise ValueError(f"Port {port} not found in available COM ports")

        matching_serial_number = None
        for ftdi_device in ftdi_devices:
            if ftdi_device.serial_number == target_port_info.serial_number[:-1]:
                matching_serial_number = ftdi_device.serial_number
                break

        if matching_serial_number is None:
            raise ValueError(
                f"No FTDI device found with serial number {target_port_info.serial_number} for port {port}"
            )

        self._open_by_serial_number(matching_serial_number)

    @staticmethod
    def __get_port_by_serial_number(serial_number: str) -> Optional[str]:
        devices_info = serial.tools.list_ports.comports()
        for device_info in devices_info:
            if device_info.serial_number is None:
                continue
            # Note: In Windows, the serial number have redundant char 'A'
            # To remove the last char 'A' from the serial number before parsing.
            if device_info.serial_number.lower()[:-1] == serial_number.lower():
                return device_info.device
        return None

    def __get_serial_number_by_port(self, port: str) -> Optional[str]:
        devices_info = serial.tools.list_ports.comports()
        for device_info in devices_info:
            if device_info.device.lower() == port.lower():
                assert device_info.serial_number is not None
                return self.__get_actual_serial_number(device_info.serial_number[:-1])
        return None

    def __get_actual_serial_number(self, serial_number: str) -> Optional[str]:
        # Note: In Windows, the serial number is case insensitive
        # but in FTDI, it is case sensitive.
        # To find the actual serial number of the FTDI device, we need to traverse with case insensitive.
        ftdi_devices = self.wrapper.get_devices_info()

        for ftdi_device in ftdi_devices:
            if ftdi_device.serial_number.lower() == serial_number.lower():
                return ftdi_device.serial_number
        return None
