from enum import IntEnum, IntFlag


class FTStatus(IntEnum):
    OK = 0
    INVALID_HANDLE = 1
    DEVICE_NOT_FOUND = 2
    DEVICE_NOT_OPENED = 3
    IO_ERROR = 4
    INSUFFICIENT_RESOURCES = 5
    INVALID_PARAMETER = 6
    INVALID_BAUD_RATE = 7
    DEVICE_NOT_OPENED_FOR_ERASE = 8
    DEVICE_NOT_OPENED_FOR_WRITE = 9
    FAILED_TO_WRITE_DEVICE = 10
    EEPROM_READ_FAILED = 11
    EEPROM_WRITE_FAILED = 12
    EEPROM_ERASE_FAILED = 13
    EEPROM_NOT_PRESENT = 14
    EEPROM_NOT_PROGRAMMED = 15
    INVALID_ARGS = 16
    NOT_SUPPORTED = 17
    OTHER_ERROR = 18
    DEVICE_LIST_NOT_READY = 19

    @classmethod
    def is_ok(cls, val: int) -> bool:
        return val == 0


class FTOpenExFlags(IntFlag):
    OPEN_BY_SERIAL_NUMBER = 0x01
    OPEN_BY_DESCRIPTION = 0x02
    OPEN_BY_LOCATION = 0x04


class FTListDevicesFlags(IntFlag):
    LIST_NUMBER_ONLY = 0x80000000
    LIST_BY_INDEX = 0x40000000
    LIST_ALL = 0x20000000


class FTDeviceListInfoNodeFlags(IntEnum):
    NONSET = 0
    FLAGS_OPENED = 1
    FLAGS_HISPEED = 2


class FTBaudRates(IntEnum):
    BAUD_300 = 300
    BAUD_600 = 600
    BAUD_1200 = 1200
    BAUD_2400 = 2400
    BAUD_4800 = 4800
    BAUD_9600 = 9600
    BAUD_14400 = 14400
    BAUD_19200 = 19200
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200
    BAUD_230400 = 230400
    BAUD_460800 = 460800
    BAUD_921600 = 921600


class FTFlowControl(IntFlag):
    NONE = 0x0000
    RTS_CTS = 0x0100
    DTR_DSR = 0x0200
    XON_XOFF = 0x0400


class FTPurge(IntFlag):
    RX = 1
    TX = 2


class FTEvent(IntFlag):
    RXCHAR = 1
    MODEM_STATUS = 2
    LINE_STATUS = 4


class FTBitMode(IntEnum):
    RESET = 0x00
    ASYNC_BITBANG = 0x01
    MPSSE = 0x02
    SYNC_BITBANG = 0x04
    MCU_HOST = 0x08
    FAST_SERIAL = 0x10
    CBUS_BITBANG = 0x20
    SYNC_FIFO = 0x40


class FT232RCBUS(IntEnum):
    TXDEN = 0x00
    PWRON = 0x01
    RXLED = 0x02
    TXLED = 0x03
    TXRXLED = 0x04
    SLEEP = 0x05
    CLK48 = 0x06
    CLK24 = 0x07
    CLK12 = 0x08
    CLK6 = 0x09
    IOMODE = 0x0A
    BITBANG_WR = 0x0B
    BITBANG_RD = 0x0C


class FT232HCBUS(IntEnum):
    TRISTATE = 0x00
    TXLED = 0x01
    RXLED = 0x02
    TXRXLED = 0x03
    PWREN = 0x04
    SLEEP = 0x05
    DRIVE_0 = 0x06
    DRIVE_1 = 0x07
    IOMODE = 0x08
    TXDEN = 0x09
    CLK30 = 0x0A
    CLK15 = 0x0B
    CLK7_5 = 0x0C


class FTXSeriesCBUS(IntEnum):
    TRISTATE = 0x00
    TXLED = 0x01
    RXLED = 0x02
    TXRXLED = 0x03
    PWREN = 0x04
    SLEEP = 0x05
    DRIVE_0 = 0x06
    DRIVE_1 = 0x07
    IOMODE = 0x08
    TXDEN = 0x09
    CLK24 = 0x0A
    CLK12 = 0x0B
    CLK6 = 0x0C
    BCD_CHARGER = 0x0D
    BCD_CHARGER_N = 0x0E
    I2C_TXE = 0x0F
    I2C_RXF = 0x10
    VBUS_SENSE = 0x11
    BITBANG_WR = 0x12
    BITBANG_RD = 0x13
    TIMESTAMP = 0x14
    KEEP_AWAKE = 0x15


class FTBits(IntEnum):
    BITS_7 = 7
    BITS_8 = 8


class FTStopBits(IntEnum):
    STOP_BITS_1 = 0
    STOP_BITS_2 = 2


class FTParity(IntEnum):
    NONE = 0
    ODD = 1
    EVEN = 2
    MARK = 3
    SPACE = 4


class FTDeviceType(IntEnum):
    BM = 0
    AM = 1
    AX100 = 2
    UNKNOWN = 3
    FT2232C = 4
    FT232R = 5
    FT2232H = 6
    FT4232H = 7
    FT232H = 8
    X_SERIES = 9
    FT4222H_0 = 10
    FT4222H_1_2 = 11
    FT4222H_3 = 12
    FT4222_PROG = 13
    FT900 = 14
    FT930 = 15
    UMFTPD3A = 16
    FT2233HP = 17
    FT4233HP = 18
    FT2232HP = 19
    FT4232HP = 20
    FT233HP = 21
    FT232HP = 22
    FT2232HA = 23
    FT4232HA = 24
    FT232RN = 25
    FT2233HPN = 26
    FT4233HPN = 27
    FT2232HPN = 28
    FT4232HPN = 29
    FT233HPN = 30
    FT232HPN = 31
    BM_A = 32


class FTDriverType(IntEnum):
    D2XX = 0
    VCP = 1


class FTTimeoutDefaults(IntEnum):
    RX = 300
    TX = 300
