from typing import Dict, Type
from .namespace import FTStatus


class FTD2XXException(Exception):
    """Base exception for FTD2XX errors."""
    pass


class FTD2XXInvalidHandleException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Invalid handle")


class FTD2XXDeviceNotFoundException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Device not found")


class FTD2XXDeviceNotOpenedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Device not opened")


class FTD2XXIOErrorException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("IO error")


class FTD2XXInsufficientResourcesException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Insufficient resources")


class FTD2XXInvalidParameterException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Invalid parameter")


class FTD2XXInvalidBaudRateException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Invalid baud rate")


class FTD2XXDeviceNotOpenedForEraseException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Device not opened for erase")


class FTD2XXDeviceNotOpenedForWriteException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Device not opened for write")


class FTD2XXFailedToWriteDeviceException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Failed to write device")


class FTD2XZEepromReadFailedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("EEPROM read failed")


class FTD2XZEepromWriteFailedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("EEPROM write failed")


class FTD2XZEepromEraseFailedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("EEPROM erase failed")


class FTD2XZEepromNotPresentException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("EEPROM not present")


class FTD2XZEepromNotProgrammedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("EEPROM not programmed")


class FTD2XXInvalidArgsException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Invalid arguments")


class FTD2XXNotSupportedException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Not supported")


class FTD2XXOtherErrorException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Other error")


class FTD2XXDeviceListNotReadyException(FTD2XXException):
    def __init__(self) -> None:
        super().__init__("Device list not ready")


# Alias for backward compatibility or logical naming
FTD2XXDeviceNotOpenException = FTD2XXDeviceNotOpenedException


STATUS_EXCEPTION_MAP: Dict[int, Type[FTD2XXException]] = {
    FTStatus.INVALID_HANDLE: FTD2XXInvalidHandleException,
    FTStatus.DEVICE_NOT_FOUND: FTD2XXDeviceNotFoundException,
    FTStatus.DEVICE_NOT_OPENED: FTD2XXDeviceNotOpenedException,
    FTStatus.IO_ERROR: FTD2XXIOErrorException,
    FTStatus.INSUFFICIENT_RESOURCES: FTD2XXInsufficientResourcesException,
    FTStatus.INVALID_PARAMETER: FTD2XXInvalidParameterException,
    FTStatus.INVALID_BAUD_RATE: FTD2XXInvalidBaudRateException,
    FTStatus.DEVICE_NOT_OPENED_FOR_ERASE: FTD2XXDeviceNotOpenedForEraseException,
    FTStatus.DEVICE_NOT_OPENED_FOR_WRITE: FTD2XXDeviceNotOpenedForWriteException,
    FTStatus.FAILED_TO_WRITE_DEVICE: FTD2XXFailedToWriteDeviceException,
    FTStatus.EEPROM_READ_FAILED: FTD2XZEepromReadFailedException,
    FTStatus.EEPROM_WRITE_FAILED: FTD2XZEepromWriteFailedException,
    FTStatus.EEPROM_ERASE_FAILED: FTD2XZEepromEraseFailedException,
    FTStatus.EEPROM_NOT_PRESENT: FTD2XZEepromNotPresentException,
    FTStatus.EEPROM_NOT_PROGRAMMED: FTD2XZEepromNotProgrammedException,
    FTStatus.INVALID_ARGS: FTD2XXInvalidArgsException,
    FTStatus.NOT_SUPPORTED: FTD2XXNotSupportedException,
    FTStatus.OTHER_ERROR: FTD2XXOtherErrorException,
    FTStatus.DEVICE_LIST_NOT_READY: FTD2XXDeviceListNotReadyException,
}


def raise_for_status(status: int) -> None:
    """
    Raise an exception if the status indicates an error.

    Args:
        status (int): The status code from the FTD2XX library.

    Raises:
        FTD2XXException: If the status indicates an error.
    """
    if FTStatus.is_ok(status):
        return

    exception_cls = STATUS_EXCEPTION_MAP.get(status)
    if exception_cls:
        raise exception_cls()

    raise FTD2XXException(f"Unknown error: {status}")
