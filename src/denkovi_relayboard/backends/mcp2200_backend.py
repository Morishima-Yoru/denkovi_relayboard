import logging
from typing import List, Optional

import serial.tools.list_ports
from .. import hid

from ..definitions.constants import MCP2200_PID, MCP_VID
from ..definitions.interfaces import IBackend
from ..definitions.structures import DiscoveredDevice

_logger = logging.getLogger(__name__)


class MCP2200Backend(IBackend):
    def __init__(self) -> None:
        self.hid_device: Optional[hid.Device] = None
        self.serial_number: Optional[str] = None
        self.timeout: int = 5000

    def open(
        self,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        """
        MCP2200 backend.

        Args:
            device_address (Optional[str]): MCP2200 vcp address, default is None.
            serial_number (Optional[str]): MCP2200 serial number, default is None.
            timeout (int): MCP2200 timeout, default is 5000.

        Raises:
            RuntimeError: If failed to open HID device.
        """

        if bool(device_address) == bool(serial_number):
            raise ValueError("Either device_address or serial_number must be provided")

        if serial_number:
            serial_number_ = serial_number
        else:
            assert device_address is not None
            serial_number_ = self.__find_serial_number(device_address)  # type: ignore[assignment]

        if serial_number_ is None:
            raise ValueError(f"Could not find serial number for device address {device_address}")

        self.timeout = timeout

        try:
            self.hid_device = hid.Device(
                vid=MCP_VID, pid=MCP2200_PID, serial=serial_number_
            )
            self.serial_number = serial_number_

        except Exception as e:
            raise RuntimeError(f"Failed to open HID device: {e}")

    def close(self) -> None:
        """
        Close MCP2200 backend.
        """
        if self.hid_device is None:
            return
        try:
            self.hid_device.close()
        except Exception as e:
            _logger.warning(f"Error closing HID device: {e}")
        finally:
            self.hid_device = None

    def write(self, data: bytes) -> None:
        """
        Write data to MCP2200 backend.

        Args:
            data (bytes): The data to write.

        Raises:
            RuntimeError: If the device is not open.
        """
        if self.hid_device is None:
            raise RuntimeError("Device is not open")

        # HID requires report ID as the first byte
        data_ = bytearray([0x00]) + bytearray(data)
        self.hid_device.write(bytes(data_))  # type: ignore
        _logger.debug(f"Write {len(data)} bytes, content: {data!r}")

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from MCP2200 backend.

        Args:
            size (Optional[int]): The size of the data to read.

        Returns:
            bytes: The data read from the MCP2200 backend.

        Raises:
            RuntimeError: If the device is not open.
        """
        if self.hid_device is None:
            raise RuntimeError("Device is not open")
        data = self.hid_device.read(size, timeout=self.timeout)  # type: ignore
        _logger.debug(f"Read {len(data)} bytes, content: {data!r}")
        return data

    @classmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        """
        List available MCP2200 devices.

        Returns:
            List[DiscoveredDevice]: A list of available MCP2200 devices.
        """
        devices: List[DiscoveredDevice] = []

        # Get all COM ports first
        com_ports = {}
        try:
            for port in serial.tools.list_ports.comports():
                if port.serial_number:
                    com_ports[port.serial_number] = port.device
        except Exception as e:
            _logger.warning(f"Failed to list COM ports: {e}")

        # MCP2200 default VID/PID
        try:
            for d in hid.enumerate(MCP_VID, MCP2200_PID):
                serial_number = d.get("serial_number")
                device_address = None

                if serial_number and serial_number in com_ports:
                    device_address = com_ports[serial_number]

                devices.append(DiscoveredDevice(
                    backend="mcp2200",
                    serial_number=serial_number,  # type: ignore[assignment]
                    device_address=device_address,  # type: ignore[assignment]
                ))
        except Exception as e:
            _logger.warning(f"Failed to list MCP2200 devices: {e}")
        return devices

    def is_open(self) -> bool:
        """
        Check if the MCP2200 backend is open.

        Returns:
            bool: True if the MCP2200 backend is open, False otherwise.
        """
        return self.hid_device is not None

    def get_serial_number(self) -> str:
        """
        Get the serial number of the MCP2200 backend.

        Returns:
            str: The serial number of the MCP2200 backend.

        Raises:
            RuntimeError: If the device is not open.
        """
        if self.hid_device is None:
            raise RuntimeError("Device is not open")

        return self.hid_device.serial

    def __find_serial_number(self, device_address: str) -> Optional[str]:
        """
        Find the serial number of the MCP2200 backend.

        Args:
            device_address (str): The device address of the MCP2200 backend.

        Returns:
            Optional[str]: The serial number of the MCP2200 backend.

        Raises:
            RuntimeError: If the device address is not found.
        """
        for device in self.list_potential_devices():
            if device["device_address"] == device_address:
                return device["serial_number"]
        return None
