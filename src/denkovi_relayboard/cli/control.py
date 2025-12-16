import argparse
import sys

from denkovi_relayboard import create_relay_board


def main() -> None:
    parser = argparse.ArgumentParser(description="Control Denkovi Relay Boards CLI")
    parser.add_argument("--board", required=True, help="Board type (e.g., denkovi_16ch, denkovi_8ch, denkovi_4ch_mcp2200)")
    parser.add_argument("--backend", required=True, help="Backend type (e.g., ftd2xx, vcp, mcp2200, pyftdi)")
    parser.add_argument("--serial_number", help="Device Serial Number")
    parser.add_argument("--port", dest="device_address", help="Device Port/Address (e.g., COM3, /dev/ttyUSB0)")
    parser.add_argument("--relay", nargs='*', type=int, default=[], help="List of relays to turn ON (1-based index). e.g. --relay 1 2. If empty, turns all OFF.")
    parser.add_argument("--off", action="store_true", help="Turn OFF the specified relays instead of turning them ON")
    args = parser.parse_args()

    if not args.serial_number and not args.device_address:
        print("Error: Either --serial_number or --port must be specified.")
        sys.exit(1)

    try:
        print(f"Connecting to {args.board} using {args.backend}...")
        board = create_relay_board(
            board_type=args.board,
            backend_type=args.backend,
            serial_number=args.serial_number,
            device_address=args.device_address
        )
        print(f"Connected. Serial: {board.get_serial_number()}")
        logic = not args.off
        relays = args.relay
        if not relays:
            # Case: --relay (empty) or not provided.
            # If relays is empty, we should turn all off.
            print("No relays specified. Turning ALL relays OFF.")
            try:
                board.set_all_states_off()
                print("All relays turned OFF.")
            except Exception as e:
                print(f"Failed to turn off relays: {e}")
        else:
            action_str = "OFF" if args.off else "ON"
            print(f"Turning {action_str} relays: {relays}")
            try:
                board.set_clear_state(logic, *relays)
                print("Command sent successfully.")
            except Exception as e:
                print(f"Failed to set relay state: {e}")

        board.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
