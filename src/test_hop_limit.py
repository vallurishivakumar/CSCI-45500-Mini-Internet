
import json
import socket
import time
from pathlib import Path

from packet import encode_packet


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"
LOG_FILE = PROJECT_DIR / "logs" / "network.log"


def run_hop_limit_test():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    r1 = config["nodes"]["R1"]

    message_id = "HL-3001"

    packet = {
        "source": "H1",
        "destination": "H2",
        "hop_limit": 1,
        "message_type": "PROBE",
        "message_id": message_id,
        "payload": "Hop limit test"
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        data = encode_packet(packet)

        sock.sendto(
            data,
            (r1["ip"], r1["port"])
        )

        print("Hop-limit test packet sent to R1.")
        print("Message ID:", message_id)
        print("Initial hop limit:", packet["hop_limit"])

        # Give R1 time to receive and process the packet.
        time.sleep(1)

        if not LOG_FILE.exists():
            print("FAIL: Network log file was not found.")
            return

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            log_lines = file.readlines()

        matching_lines = [
            line for line in log_lines
            if message_id in line
        ]

        drop_found = any(
            "DROP" in line and "Hop limit exhausted" in line
            for line in matching_lines
        )

        print("\nTest result:")

        if drop_found:
            print("PASS: R1 correctly dropped the packet.")
            print("Reason: Hop limit exhausted.")

            for line in matching_lines:
                print(line.strip())
        else:
            print("FAIL: Expected hop-limit DROP was not found.")
            print("Matching log entries:")
            for line in matching_lines:
                print(line.strip())

    finally:
        sock.close()


if __name__ == "__main__":
    run_hop_limit_test()
