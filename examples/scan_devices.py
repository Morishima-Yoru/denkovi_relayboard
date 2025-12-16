"""
Example script to scan for available Denkovi relay boards.
This script uses the `list_potential_boards` function to find connected devices.
"""

import denkovi_relayboard as drb

def main() -> None:
    print("Scanning for connected Denkovi relay boards...")
    
    try:
        potential_boards = drb.list_potential_boards()
        
        if not potential_boards:
            print("No devices found.")
            print("Please check your USB connections and ensure drivers are installed.")
        else:
            print(f"Found {len(potential_boards)} device(s):")
            for i, device in enumerate(potential_boards, 1):
                print(f"\nDevice #{i}:")
                # DiscoveredDevice usually contains serial_number, device_address, and backend type
                print(f"  Backend:       {device.get('backend')}")
                print(f"  Serial Number: {device.get('serial_number')}")
                print(f"  Address:       {device.get('device_address')}")
            
            print("\nYou can use the 'serial_number' or 'device_address' from above")
            print("to initialize a specific board using `create_relay_board`.")
            
    except Exception as e:
        print(f"An error occurred during discovery: {e}")

if __name__ == "__main__":
    main()
