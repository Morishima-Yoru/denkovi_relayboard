from typing_extensions import Final
from typing import Callable, Optional, Set, Tuple, Union, no_type_check, TYPE_CHECKING
from contextlib import suppress
from pathlib import Path
import logging

import ctypes as ct

from .definitions.structures import FTDeviceListInfoNodeStruct
from .definitions.c_structures import FT_DEVICE_LIST_INFO_NODE
from .definitions.exceptions import FTD2XXDeviceNotOpenException, raise_for_status
from .definitions.namespace import (
    FTDeviceType,
    FTListDevicesFlags,
    FTOpenExFlags,
)

_logger = logging.getLogger(__name__)


class PyFTD2XXWrapper:
    DEFAULT_LIB_DPTH: Final = Path(__file__).parent
    POSSIBLE_LIB_FNAME: Final[Set[str]] = {
        "FTD2XX64.dll",
        "ftd2xx.dll",
        "libftd2xx.so",
        "libftd2xx.dylib",
    }

    def __init__(self, lib_fpth: Optional[Union[Path, str]] = None):
        self._dllobj: ct.CDLL
        self.__load_cdll(lib_fpth)
        self.__construct_alias()

        self._handle: Optional[ct.c_void_p] = None
        self.__serial_number: Optional[str] = None
        self.__id_: Optional[int] = None
        self.__description: Optional[str] = None
        self.__ft_type: Optional[FTDeviceType] = None

    def __load_cdll(self, specificed_fpth: Optional[Union[Path, str]] = None) -> None:
        # If specificed
        if specificed_fpth is not None and Path(specificed_fpth).is_file():
            self._dllobj = ct.CDLL(str(specificed_fpth))
            _logger.debug(f"Loaded FTD2XX library from: {specificed_fpth}")
            return

        # Try purely to load which is implicated enviroment variable
        for lib_fname in self.POSSIBLE_LIB_FNAME:
            with suppress(OSError):
                self._dllobj = ct.CDLL(str(lib_fname))
                _logger.debug(f"Loaded FTD2XX library from: {lib_fname}")
                return

        # Try with traverse whole library root.
        for lib_fname in self.POSSIBLE_LIB_FNAME:
            for lib_full_path in self.DEFAULT_LIB_DPTH.rglob(lib_fname):
                with suppress(OSError):
                    self._dllobj = ct.CDLL(str(lib_full_path))
                    _logger.debug(f"Loaded FTD2XX library from: {lib_full_path}")
                    return

        raise FileNotFoundError("Could not find FTD2XX library in the specified path.")

    def is_open(self) -> bool:
        """
        Check if the FTD2XX device is open.

        Returns:
            bool: True if the device is open, False otherwise.
        """
        return self._handle is not None

    def ft_open(self, device_idx: int) -> None:
        """
        Open the FTD2XX device.

        Args:
            device_idx (int): The index of the device.

        Raises:
            FTD2XXException: If the operation fails.
        """
        handle: ct.c_void_p = ct.c_void_p()
        st: int = self.__FT_Open(
            ct.c_int(device_idx),
            ct.byref(handle)  # type: ignore
        )
        raise_for_status(st)
        self._handle = handle
        self.__handle_session_information()

    def ft_close(self) -> None:
        """
        Close the FTD2XX device.

        Raises:
            FTD2XXException: If the operation fails.
        """
        if self._handle is None:
            raise FTD2XXDeviceNotOpenException()
        st: int = self.__FT_Close(ct.cast(self._handle, ct.POINTER(ct.c_void_p)))
        raise_for_status(st)
        self._handle = None
        self.__serial_number = None
        self.__id_ = None
        self.__description = None
        self.__ft_type = None

    def ft_set_baudrate(self, baudrate: int) -> None:
        """
        Set the baudrate of the FTD2XX device.

        Args:
            baudrate (int): The baudrate to set.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        handle_ = ct.cast(self._handle, ct.POINTER(ct.c_void_p))
        st: int = self.__FT_SetBaudRate(handle_, ct.c_uint32(baudrate))
        raise_for_status(st)

    def get_avaliable_device_count(self) -> int:
        """
        Get the number of available devices.

        Returns:
            int: The number of available devices.
        """
        ret: ct.c_void_p = ct.c_void_p()
        st: int = self.__FT_ListDevices(
            ct.byref(ret),  # type: ignore
            None,
            ct.c_uint32(FTListDevicesFlags.LIST_NUMBER_ONLY),
        )
        raise_for_status(st)
        return ret.value or 0

    def __create_device_info_list(self) -> int:
        """
        Create the device information list of the FTD2XX device.

        Returns:
            int: The number of devices.
        """
        ret: ct.c_uint32 = ct.c_uint32()
        st: int = self.__FT_CreateDeviceInfoList(ct.byref(ret))  # type: ignore
        raise_for_status(st)
        return ret.value

    def __get_device_info_list(self):
        """
        Get the device information list of the FTD2XX device.

        Returns:
            tuple[FTDeviceListInfoNodeStruct, ...]: The device information list.
        """
        num_devices_ = self.__create_device_info_list()
        container_: ct.Array[FT_DEVICE_LIST_INFO_NODE] = (
            FT_DEVICE_LIST_INFO_NODE * num_devices_
        )()
        st = self.__FT_GetDeviceInfoList(
            container_,
            ct.byref(ct.c_uint32(num_devices_))  # type: ignore
        )
        raise_for_status(st)
        return container_

    def get_devices_info(self) -> Tuple[FTDeviceListInfoNodeStruct, ...]:
        """
        Get the device information list of the FTD2XX device.

        Returns:
            tuple[FTDeviceListInfoNodeStruct, ...]: The device information list.
        """
        return tuple(
            FTDeviceListInfoNodeStruct.from_structure(itr)
            for itr in self.__get_device_info_list()
        )

    def __handle_session_information(self) -> None:
        assert self._handle
        pft_type: ct.c_uint32 = ct.c_uint32()
        lpdw_id: ct.c_uint32 = ct.c_uint32()
        pc_serial_number: ct.Array[ct.c_char] = ct.create_string_buffer(16)
        pc_description: ct.Array[ct.c_char] = ct.create_string_buffer(64)
        st = self.__FT_GetDeviceInfo(
            ct.cast(self._handle, ct.POINTER(ct.c_void_p)),
            ct.byref(pft_type),  # type: ignore
            ct.byref(lpdw_id),  # type: ignore
            pc_serial_number,
            pc_description,
            None,
        )
        raise_for_status(st)
        self.__ft_type = FTDeviceType(pft_type.value)
        self.__id_ = lpdw_id.value
        self.__serial_number = pc_serial_number.value.decode()
        self.__description = pc_description.value.decode()

    @property
    def serial_number(self) -> str:
        if self._handle is None:
            raise FTD2XXDeviceNotOpenException()
        return self.__serial_number or ""

    @property
    def description(self) -> str:
        if self._handle is None:
            raise FTD2XXDeviceNotOpenException()
        return self.__description or ""

    @property
    def ft_type(self) -> FTDeviceType:
        if self._handle is None:
            raise FTD2XXDeviceNotOpenException()
        assert self.__ft_type
        return self.__ft_type

    @property
    def id_(self) -> int:
        if self._handle is None:
            raise FTD2XXDeviceNotOpenException()
        assert self.__id_
        return self.__id_

    def ft_open_by_description(self, description: str) -> None:
        """
        Open a device by description.

        Args:
            description (str): The description (device name) of the device to open.

        Raises:
            FTD2XXException: If the operation fails.
        """
        pvarg_ = ct.create_string_buffer(description.encode())
        self.__ft_open_ex(
            pvarg=ct.byref(pvarg_),  # type: ignore
            dwflags=ct.c_uint32(FTOpenExFlags.OPEN_BY_DESCRIPTION.value),
        )

    def ft_open_by_serial_number(self, serial_number: str) -> None:
        """
        Open a device by serial number.

        Args:
            serial_number (str): The serial number of the device to open.

        Raises:
            FTD2XXException: If the operation fails.
        """
        pvarg_ = ct.create_string_buffer(serial_number.encode())
        self.__ft_open_ex(
            pvarg=ct.byref(pvarg_),  # type: ignore
            dwflags=ct.c_uint32(FTOpenExFlags.OPEN_BY_SERIAL_NUMBER.value),
        )

    def get_queue_status(self) -> int:
        """
        Get the queue status of the FTD2XX device.

        Returns:
            int: The queue status.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        ret: ct.c_uint32 = ct.c_uint32()
        st_ = self.__FT_GetQueueStatus(ct.cast(self._handle, ct.POINTER(ct.c_void_p)), ct.byref(ret))  # type: ignore
        raise_for_status(st_)
        return ret.value

    def set_timeout(self, ms_tx: int, ms_rx: int) -> None:
        """
        Set the timeout of the FTD2XX device.

        Args:
            ms_tx (int): The timeout for sending data.
            ms_rx (int): The timeout for receiving data.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        st = self.__FT_SetTimeouts(
            ct.cast(self._handle, ct.POINTER(ct.c_void_p)),
            ct.c_uint32(ms_rx),
            ct.c_uint32(ms_tx),
        )
        raise_for_status(st)

    def set_data_characteristics(
        self,
        bits: int,
        stop_bits: int,
        parity: int
    ) -> None:
        """
        Set the data characteristics of the FTD2XX device.

        Args:
            bits (int): The number of bits.
            stop_bits (int): The number of stop bits.
            parity (int): The parity.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        st = self.__FT_SetDataCharacteristics(
            ct.cast(self._handle, ct.POINTER(ct.c_void_p)),
            ct.c_ushort(bits),
            ct.c_ushort(stop_bits),
            ct.c_ushort(parity),
        )
        raise_for_status(st)

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from the FTD2XX device.

        Args:
            size (int | None): The number of bytes to read.

        Returns:
            bytes: The data read.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        if size is None:
            size = self.get_queue_status()
            if size == 0:
                return b""

        rx_p = ct.c_void_p()
        handle_ = ct.cast(self._handle, ct.POINTER(ct.c_void_p))
        bytes_read_: ct.c_uint32 = ct.c_uint32()
        st = self.__FT_Read(
            handle_,
            ct.byref(rx_p),  # type: ignore
            ct.c_uint32(size),
            ct.byref(bytes_read_),  # type: ignore
        )
        raise_for_status(st)

        ret_: bytes
        if rx_p.value:
            ret_ = rx_p.value.to_bytes(bytes_read_.value, "little")
        else:
            ret_ = b"\x00" * bytes_read_.value
        return ret_

    def write(self, data: bytes, bytes_to_write: Optional[int] = None) -> None:
        """
        Write data to the FTD2XX device.

        Args:
            data (bytes): The data to write.
            bytes_to_write (int | None): The number of bytes to write.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        tx_ = ct.create_string_buffer(data)
        size_ = bytes_to_write or (
            ct.sizeof(tx_) - 1
        )  # Negative 1 to eliminate the null terminator from `create_string_buffer(...)`
        tx_p = ct.cast(ct.pointer(tx_), ct.POINTER(ct.c_void_p))
        handle_ = ct.cast(self._handle, ct.POINTER(ct.c_void_p))
        bytes_written_: ct.c_uint32 = ct.c_uint32()
        st = self.__FT_Write(
            handle_,
            tx_p,
            ct.c_uint32(size_),
            ct.byref(bytes_written_)  # type: ignore
        )
        raise_for_status(st)

    def set_bit_mode(self, mask: int, mode: int) -> None:
        """
        Set the bit mode of the FTD2XX device.

        Args:
            mask (int): The mask.
            mode (int): The mode.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        mask_ = ct.c_ubyte(mask)
        mode_ = ct.c_ubyte(mode)
        st = self.__FT_SetBitMode(
            ct.cast(self._handle, ct.POINTER(ct.c_void_p)), mask_, mode_
        )
        raise_for_status(st)

    def get_bit_mode(self) -> int:
        """
        Get the bit mode of the FTD2XX device.

        Returns:
            int: The GPIO bit status.

        Raises:
            FTD2XXException: If the operation fails.
        """
        assert self._handle
        ret: ct.c_ubyte = ct.c_ubyte()
        st = self.__FT_GetBitMode(
            ct.cast(self._handle, ct.POINTER(ct.c_void_p)),
            ct.byref(ret)  # type: ignore
        )  # type: ignore
        raise_for_status(st)
        return ret.value

    def __ft_open_ex(self, pvarg: ct.c_void_p, dwflags: ct.c_uint32) -> None:
        """
        Open the FTD2XX device with the given parameters.

        Args:
            pvarg (ct.c_void_p): The parameters.
            dwflags (ct.c_uint32): The flags.

        Raises:
            FTD2XXException: If the operation fails.
        """
        handle_: ct.c_void_p = ct.c_void_p()
        st: int = self.__FT_OpenEx(pvarg, dwflags, ct.byref(handle_))  # type: ignore
        raise_for_status(st)
        self._handle = handle_

    def __del__(self) -> None:
        with suppress(Exception):
            self.ft_close()

    def __construct_alias(self) -> None:
        self.__FT_Open = self._dllobj.FT_Open
        self.__FT_Close = self._dllobj.FT_Close
        self.__FT_ListDevices = self._dllobj.FT_ListDevices
        self.__FT_CreateDeviceInfoList = self._dllobj.FT_CreateDeviceInfoList
        self.__FT_GetDeviceInfoList = self._dllobj.FT_GetDeviceInfoList
        self.__FT_GetDeviceInfo = self._dllobj.FT_GetDeviceInfo
        self.__FT_Write = self._dllobj.FT_Write
        self.__FT_Read = self._dllobj.FT_Read
        self.__FT_OpenEx = self._dllobj.FT_OpenEx
        self.__FT_SetBaudRate = self._dllobj.FT_SetBaudRate
        self.__FT_GetStatus = self._dllobj.FT_GetStatus
        self.__FT_GetQueueStatus = self._dllobj.FT_GetQueueStatus
        self.__FT_SetTimeouts = self._dllobj.FT_SetTimeouts
        self.__FT_SetBitMode = self._dllobj.FT_SetBitMode
        self.__FT_GetBitMode = self._dllobj.FT_GetBitMode
        self.__FT_SetDataCharacteristics = self._dllobj.FT_SetDataCharacteristics

        self.__FT_Open.argtypes = (ct.c_int, ct.POINTER(ct.c_void_p))
        self.__FT_Open.restype = ct.c_uint32
        self.__FT_OpenEx.argtypes = (ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_void_p))
        self.__FT_OpenEx.restype = ct.c_uint32
        self.__FT_Close.argtypes = (ct.POINTER(ct.c_void_p),)
        self.__FT_Close.restype = ct.c_uint32
        self.__FT_CreateDeviceInfoList.argtypes = (ct.POINTER(ct.c_uint32),)
        self.__FT_CreateDeviceInfoList.restype = ct.c_uint32
        self.__FT_GetDeviceInfoList.argtypes = (
            ct.POINTER(FT_DEVICE_LIST_INFO_NODE),
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_GetDeviceInfoList.restype = ct.c_uint32
        self.__FT_ListDevices.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_void_p),
            ct.c_uint32,
        )
        self.__FT_ListDevices.restype = ct.c_uint32
        self.__FT_GetDeviceInfo.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_uint32),
            ct.POINTER(ct.c_uint32),
            ct.Array,
            ct.Array,
            ct.c_void_p,
        )
        self.__FT_GetDeviceInfo.restype = ct.c_uint32
        self.__FT_Write.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_void_p),
            ct.c_uint32,
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_Write.restype = ct.c_uint32
        self.__FT_Read.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_void_p),
            ct.c_uint32,
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_Read.restype = ct.c_uint32
        self.__FT_SetBaudRate.argtypes = (ct.c_void_p, ct.c_uint32)
        self.__FT_SetBaudRate.restype = ct.c_uint32
        self.__FT_GetQueueStatus.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_GetQueueStatus.restype = ct.c_uint32
        self.__FT_GetStatus.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_uint32),
            ct.POINTER(ct.c_uint32),
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_GetStatus.restype = ct.c_uint32
        self.__FT_GetQueueStatus.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_uint32),
        )
        self.__FT_GetQueueStatus.restype = ct.c_uint32
        self.__FT_SetTimeouts.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.c_uint32,
            ct.c_uint32,
        )
        self.__FT_SetTimeouts.restype = ct.c_uint32
        self.__FT_SetDataCharacteristics.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.c_ushort,
            ct.c_ushort,
            ct.c_ushort,
        )
        self.__FT_SetDataCharacteristics.restype = ct.c_uint32
        self.__FT_SetBitMode.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.c_ubyte,
            ct.c_ubyte,
        )
        self.__FT_SetBitMode.restype = ct.c_uint32
        self.__FT_GetBitMode.argtypes = (
            ct.POINTER(ct.c_void_p),
            ct.POINTER(ct.c_ubyte),
        )
        self.__FT_GetBitMode.restype = ct.c_uint32

    if TYPE_CHECKING:
        @no_type_check
        def __type_hintting(self) -> None:
            # Section makes various alias for ONLY type-hintting purposes.
            self.__FT_Open: Callable[[ct.c_int, ct.c_void_p], int]
            self.__FT_OpenEx: Callable[[ct.c_void_p, ct.c_uint32, ct.c_void_p], int]
            self.__FT_Close: Callable[[ct._Pointer[ct.c_void_p]], int]
            self.__FT_ListDevices: Callable[
                [Optional[ct.c_void_p], Optional[ct.c_void_p], ct.c_uint32], int
            ]
            self.__FT_GetDeviceInfo: Callable[
                [
                    ct._Pointer[ct.c_void_p],
                    Optional[ct._Pointer[ct.c_uint32]],
                    Optional[ct._Pointer[ct.c_uint32]],
                    ct.Array[ct.c_char],
                    ct.Array[ct.c_char],
                    None,
                ],
                int,
            ]
            self.__FT_CreateDeviceInfoList: Callable[[ct._Pointer[ct.c_uint32]], int]
            self.__FT_Write: Callable[
                [
                    ct._Pointer[ct.c_void_p],
                    ct._Pointer[ct.c_void_p],
                    ct.c_uint32,
                    ct._Pointer[ct.c_uint32],
                ],
                int,
            ]
            self.__FT_Read: Callable[
                [
                    ct._Pointer[ct.c_void_p],
                    ct._Pointer[ct.c_void_p],
                    ct.c_uint32,
                    ct._Pointer[ct.c_uint32],
                ],
                int,
            ]
            self.__FT_GetStatus: Callable[
                [
                    ct._Pointer[ct.c_void_p],
                    ct._Pointer[ct.c_uint32],
                    ct._Pointer[ct.c_uint32],
                    ct._Pointer[ct.c_uint32],
                ],
                int,
            ]
            self.__FT_GetDeviceInfoList: Callable[
                [ct.Array[FT_DEVICE_LIST_INFO_NODE], ct._Pointer[ct.c_uint32]], int
            ]
            self.__FT_SetBaudRate: Callable[[ct._Pointer[ct.c_void_p], ct.c_uint32], int]
            self.__FT_GetQueueStatus: Callable[
                [ct._Pointer[ct.c_void_p], ct._Pointer[ct.c_uint32]], int
            ]
            self.__FT_SetTimeouts: Callable[
                [ct._Pointer[ct.c_void_p], ct.c_uint32, ct.c_uint32], int
            ]
            self.__FT_SetDataCharacteristics: Callable[
                [ct._Pointer[ct.c_void_p], ct.c_ushort, ct.c_ushort, ct.c_ushort], int
            ]
            self.__FT_SetBitMode: Callable[
                [ct._Pointer[ct.c_void_p], ct.c_ubyte, ct.c_ubyte], int
            ]
            self.__FT_GetBitMode: Callable[
                [ct._Pointer[ct.c_void_p], ct._Pointer[ct.c_ubyte]], int
            ]
