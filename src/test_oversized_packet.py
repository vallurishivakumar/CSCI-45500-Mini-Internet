
import socket
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "logs" / "network.log"

def run_test():
    router_address = ("127.0.0.1", 5002)

    # Send a UDP datagram larger than the 1200-byte limit.
    oversized_packet = b"A" * 1300
    message_marker = "oversized"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(oversized_packet, router_address)

        print("Oversized packet sent to R1.")
        print("Packet size:", len(oversized_packet), "bytes")

        time.sleep(1)

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = file.read()

        if "oversized" in logs.lower() or "too large" in logs.lower():
            print("\nPASS: Oversized packet rejection was logged.")
        else:
            print("\nCheck the R1 terminal and network log.")
            print("We need to verify that R1 rejected the packet.")

    finally:
        sock.close()


if __name__ == "__main__":
    run_test()
