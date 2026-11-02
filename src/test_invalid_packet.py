
import socket
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "logs" / "network.log"


def run_test():
    router_address = ("127.0.0.1", 5002)

    # This packet is intentionally missing required fields.
    invalid_packet = b'{"source":"H1","destination":"H2"}'

    message_marker = "Invalid packet test"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(invalid_packet, router_address)

        print("Invalid packet sent to R1.")
        time.sleep(1)

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = file.read()

        if "INVALID" in logs.upper() or "invalid" in logs.lower():
            print("\nCheck the router terminal and network log.")
            print("Look for an invalid-packet rejection message.")
        else:
            print("\nNo invalid-packet log entry found.")
            print("Check whether your router logs malformed packets.")

    finally:
        sock.close()


if __name__ == "__main__":
    run_test()
