import logging
import time
from denkovi_relayboard import create_relay_board

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def main():
    # Example configuration for an 8-channel relay board
    # You might need to adjust 'serial_number' or use 'device_address' depending on your setup
    # Use `uv run denkovi_relayboard/test_discovery.py` or similar to find your device details
    
    # Try to connect to a device. 
    print("Connecting to relay board...")
    try:
        # Example: 8-channel board using ftd2xx backend
        board = create_relay_board(
            board_type='denkovi_8ch',
            backend_type='ftd2xx',
            serial_number="DAE06LpX",  # Replace with your device's serial number
            # Or use device_address
            # device_address='COM14',  # e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux
            timeout=5000
        )
        
        # Or Example: 4-channel board using MCP2200 backend
        # board = create_relay_board(
        #     board_type='denkovi_4ch_mcp2200',
        #     backend_type='mcp2200',
        #     serial_number="0003639685",
        #     timeout=5000
        # )

    except Exception as e:
        print(f"Failed to create board: {e}")
        print("Please ensure your device is connected and the configuration matches your hardware.")
        return

    try:
        print(f"Connected! Serial Number: {board.get_serial_number()}")
        
        # Turn off all relays initially
        print("Turning all relays OFF...")
        board.set_all_states_off()
        time.sleep(1)

        # Iterate through relays and turn them on one by one
        print("Cycling relays...")
        for i in range(1, board.max_channel + 1):
            print(f"Turning ON relay {i}")
            board.set_state(True, i)
            time.sleep(0.5)
            print(f"Turning OFF relay {i}")
            board.set_state(False, i)
            time.sleep(0.2)

        # Demonstrate multiple relay control
        print("Turning ON relays 1 and 2...")
        board.set_state(True, 1, 2)
        print(f"Current States: {board.get_all_states()}")
        time.sleep(1)
        
        print("Turning OFF all relays...")
        board.set_all_states_off()

    except Exception as e:
        print(f"An error occurred during operation: {e}")
    finally:
        print("Closing connection...")
        board.close()

if __name__ == "__main__":
    main()
