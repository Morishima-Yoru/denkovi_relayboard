# Denkovi Relay Board Control Library

A Python library for controlling Denkovi USB relay boards using various backends (FTD2XX, PyFtdi, VCP, MCP2200/HID).

## Features

- **Multiple Backends**: Support for different connection methods:
  - `ftd2xx`: Native FTDI D2XX driver (requires system drivers).
  - `pyftdi`: Pure Python libusb-based FTDI driver.
  - `vcp`: Virtual COM Port (Serial).
  - `mcp2200`: HID-based control for MCP2200 chips.
- **Unified API**: Control different boards with a consistent interface.
- **CLI Tools**: Built-in command-line tools for listing devices and basic control.

## Installation

### From Source

```bash
pip install .
```

### Prerequisites

Depending on the backend you choose, you may need additional drivers:

- **ftd2xx**: Requires the FTDI D2XX drivers installed on your system.
  - Windows: `ftd2xx.dll` (usually installed with FTDI drivers).
  - Linux: `libftd2xx.so`.
- **pyftdi**: Requires `libusb` installed on your system.
- **mcp2200**: Uses HIDAPI (shared libraries are bundled for common platforms in `src/denkovi_relayboard/hid/bin`).

## Usage

### Python API

```python
import time
from denkovi_relayboard import create_relay_board

# Create a relay board instance
# Example for a 4-channel board using FTD2XX backend
board = create_relay_board(
    board_type='denkovi_8ch,
    backend_type='ftd2xx',
    serial_number='DAE06LpX',  # Replace with your device serial number
)

try:
    # Turn ON relay 1
    board.set_state(True, 1)
    print("Relay 1 is ON")
    time.sleep(1)

    # Turn OFF relay 1
    board.set_state(False, 1)
    print("Relay 1 is OFF")
    
    # Turn ON all relays
    board.set_all_states_on()
    time.sleep(1)
    
    # Turn OFF all relays
    board.set_all_states_off()

finally:
    board.close()
```

### Command Line Interface (CLI)

The package provides two CLI commands:

**1. List available devices:**

```bash
list_potential_device
```

Output example:
```
Scanning for connected Denkovi relay boards...
Found 6 device(s):
  Device #1:
    Backend:       ftd2xx
    Serial Number: DAE06LpX
    Address:       COM12
  Device #2:
    Backend:       ftd2xx
    Serial Number: DAE006E8
    Address:       COM14
  Device #3:
    Backend:       vcp
    Serial Number: DAE06LPXA
    Address:       COM12
  Device #4:
    Backend:       vcp
    Serial Number: 0003639685
    Address:       COM13
  Device #5:
    Backend:       vcp
    Serial Number: DAE006E8A
    Address:       COM14
  Device #6:
    Backend:       mcp2200
    Serial Number: 0003639685
    Address:       COM13
```

**2. Control a device:**

```bash
control_denkovi --board denkovi_16ch --backend vcp --serial DAE006E8 --relay 1 2 3
```

## Supported Boards

- Denkovi 4 Channel USB Relay Board (MCP2200)
- Denkovi 4 Channel USB Relay Board (FTDI) (Untested)
- Denkovi 8 Channel USB Relay Board
- Denkovi 16 Channel USB Relay Board

## Note
* It is recommand to use PyFtdi backend if the operation system is Linux, and FTD2XX backend in Windows.
* When using FTD2XX backend in Linux, you need to install the FTDI D2XX driver and `sudo rmmod ftdi_sio` first.
For more information, please refer to the [FTDI D2XX for Linux](https://ftdichip.com/Driver/D2XX/Linux/ReadMe.txt).
* When using PyFtdi backend in Windows, you need to install `libusb-win32` to the device with Zadig first.
For more information, please refer to the [PyFtdi Installation](https://eblot.github.io/pyftdi/installation.html).

## License

MIT License

