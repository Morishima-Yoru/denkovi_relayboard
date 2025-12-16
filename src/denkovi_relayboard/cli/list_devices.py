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
                print(
                    f"  Device #{i}:\n"
                    f"    Backend:       {device.get('backend')}\n"
                    f"    Serial Number: {device.get('serial_number')}\n"
                    f"    Address:       {device.get('device_address')}"
                )

            print(
                "\nYou can use the 'serial_number' or 'device_address' from above\n"
                "to initialize a specific board using `create_relay_board` or `control_denkovi` tool."
            )

    except Exception as e:
        print(f"An error occurred during discovery: {e}")


if __name__ == "__main__":
    main()
