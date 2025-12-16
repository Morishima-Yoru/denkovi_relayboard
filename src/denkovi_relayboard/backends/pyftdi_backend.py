import atexit
import weakref
from typing_extensions import Final
from typing import List, Optional
import logging
import time

import serial.tools.list_ports
from pyftdi.ftdi import Ftdi

from ..definitions.constants import (
    DEFAULT_BAUD_RATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOP_BITS,
    FT232H_PID,
    FT232R_PID,
    FTDI_VID
)
from ..definitions.structures import DiscoveredDevice
from ..definitions.interfaces import IBackend

_logger = logging.getLogger(__name__)


class PyFtdiBackend(IBackend):
    __PARITY_NAME_MAP: Final = {
        "none": "N",
        "even": "E",
        "odd": "O",
        "mark": "M",
        "space": "S",
    }
    # Pyftdi uses 1, 1.5, 2 as stop bits values (float or int)
    __STOP_BITS_NAME_MAP: Final = {1: 1, 2: 2}

    def __init__(self) -> None:
        self.ftdi: Ftdi = Ftdi()
        self.serial_number: Optional[str] = None
        self.timeout: int = 5000
        self.is_opened: bool = False

    def open(
        self,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> None:
        """
        Open PyFtdi backend.

        Args:
            device_address (Optional[str]): The device address (URL or port).
            serial_number (Optional[str]): The serial number.
            timeout (int): The timeout in milliseconds (default 5000).

        Raises:
            ValueError: If the device_address and serial_number are both provided.
            ValueError: If the device_address and serial_number are both not provided.
            ValueError: If the serial_number is not found.
        """
        if bool(device_address) == bool(serial_number):
            raise ValueError("Either device_address or serial_number must be provided for PyFtdi backend")

        if device_address is not None:
            self.port = device_address

            # Find serial number from port
            ports = serial.tools.list_ports.comports()
            for port_info in ports:
                if port_info.device == device_address:
                    serial_number = port_info.serial_number
                    break

            if not serial_number:
                raise ValueError(f"Could not find serial number for device {device_address}")

        # Try to find the device first to get correct VID/PID
        try:
            # This finds all FTDI devices
            dev_list = Ftdi.find_all((
                (FTDI_VID, FT232R_PID),
                (FTDI_VID, FT232H_PID))
            )
            for dev in dev_list:
                # dev is (UsbDeviceDescriptor, interface_count)
                descriptor = dev[0]
                if descriptor.sn != serial_number:
                    continue
                self.ftdi.open(
                    descriptor.vid,
                    descriptor.pid,
                    serial=descriptor.sn,
                    interface=1,
                )
                self.is_opened = True
                break
        except Exception as e:
            _logger.warning(f"Failed to search for device: {e}")

        self.serial_number = serial_number
        self.__register_exit_handler()

        self.ftdi.reset()
        self.ftdi.set_bitmode(0, Ftdi.BitMode.RESET)
        self.ftdi.set_baudrate(DEFAULT_BAUD_RATE)
        self.ftdi.set_line_property(
            bits=DEFAULT_BYTESIZE,
            stopbit=self.__STOP_BITS_NAME_MAP[DEFAULT_STOP_BITS],
            parity=self.__PARITY_NAME_MAP[DEFAULT_PARITY],
        )
        self.ftdi.timeouts = (self.timeout, self.timeout)
        self.timeout = timeout

        # HACK: Send dummy byte to awake the board, otherwise it will not respond in the first time.
        self.ftdi.write_data(b"\x00")
        self.ftdi.purge_buffers()

    def close(self) -> None:
        """
        Close PyFtdi backend.
        """
        if self.is_opened:
            try:
                self.ftdi.close()
            except Exception as e:
                _logger.warning(f"Error closing PyFtdi backend: {e}")
            finally:
                self.is_opened = False

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def write(self, data: bytes) -> None:
        """
        Write data to PyFtdi backend.

        Args:
            data (bytes): The data to write.

        Raises:
            RuntimeError: If failed to write.
        """
        try:
            written_ = self.ftdi.write_data(data)
            _logger.debug(f"Write {written_} bytes, content: {data!r}")
        except Exception as e:
            raise RuntimeError(f"Failed to write: {e}")

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from PyFtdi backend.

        Args:
            size (Optional[int]): The size of the data to read.

        Returns:
            bytes: The data read from the PyFtdi backend.

        Raises:
            RuntimeError: If failed to read.
        """
        try:
            if size is None:
                size = self.ftdi.read_data_get_chunksize()
                ret_ = self.ftdi.read_data(size)
                _logger.debug(f"Read {len(ret_)} bytes, content: {ret_!r}")
                return ret_

            data = b""
            start_time = time.time()
            while len(data) < size:
                chunk = self.ftdi.read_data(size - len(data))
                if chunk:
                    data += chunk

                if len(data) >= size:
                    break

                if (time.time() - start_time) * 1000 > self.timeout:
                    break

                time.sleep(0.005)

            _logger.debug(f"Read {len(data)} bytes, content: {data!r}")
            return data

        except Exception as e:
            raise RuntimeError(f"Failed to read: {e}")

    def is_open(self) -> bool:
        """
        Check if the PyFtdi backend is open.

        Returns:
            bool: True if the PyFtdi backend is open, False otherwise.
        """
        return self.is_opened

    def get_serial_number(self) -> str:
        """
        Get the serial number of the PyFtdi backend.

        Returns:
            str: The serial number of the PyFtdi backend.
        """
        if self.serial_number:
            return self.serial_number
        if self.is_opened and self.ftdi.usb_dev:
            return self.ftdi.usb_dev.serial_number  # type: ignore
        return ""

    def set_bit_mode(self, mask: int, mode: int) -> None:
        """
        Set the bit mode of the PyFtdi backend.

        Args:
            mask (int): The mask.
            mode (int): The mode.

        Raises:
            RuntimeError: If failed to set bit mode.
        """
        mode_enum_ = Ftdi.BitMode(mode)
        try:
            self.ftdi.set_bitmode(mask, mode_enum_)
            _logger.debug(f"Set bit mode: {mask}, {mode_enum_}")
        except Exception as e:
            raise RuntimeError(f"Failed to set bit mode: {e}")

    def get_bit_mode(self) -> int:
        """
        Get the bit mode of the PyFtdi backend.

        Returns:
            int: The GPIO bit status.

        Raises:
            RuntimeError: If failed to get bit mode.
        """
        try:
            # read_pins returns the byte value of the pins
            ret_ = self.ftdi.read_pins()
            _logger.debug(f"Get bit mode: {ret_}")
            return ret_
        except Exception as e:
            raise RuntimeError(f"Failed to get bit mode: {e}")

    @classmethod
    def list_potential_devices(cls) -> List[DiscoveredDevice]:
        """
        List potential PyFtdi devices.

        Returns:
            List[DiscoveredDevice]: A list of potential PyFtdi devices.
        """
        devices: List[DiscoveredDevice] = []
        try:
            ports = serial.tools.list_ports.comports()
            sn_to_port = {p.serial_number: p.device for p in ports if p.serial_number}

            devs = Ftdi.find_all((
                (FTDI_VID, FT232R_PID),
                (FTDI_VID, FT232H_PID))
            )
            for dev in devs:
                descriptor = dev[0]
                devices.append(DiscoveredDevice(
                    backend="pyftdi",
                    serial_number=descriptor.sn,
                    device_address=sn_to_port.get(descriptor.sn) if descriptor.sn else None,
                ))
        except Exception as e:
            _logger.warning(f"Failed to list PyFtdi devices: {e}")
        return devices

    def __register_exit_handler(self) -> None:
        """
        Register exit handler to close the PyFtdi backend.
        """
        weakref.finalize(self, self.close)
        atexit.register(self.close)
