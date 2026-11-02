
import json
import socket
import time
from pathlib import Path

from packet import encode_packet


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"
LOG_FILE = PROJECT_DIR / "logs" / "network.log"


def run_test():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    r1 = config["nodes"]["R1"]
    message_id = "UNKNOWN-4001"

    packet = {
        "source": "H1",
        "destination": "UNKNOWN",
        "hop_limit": 8,
        "message_type": "PROBE",
        "message_id": message_id,
        "payload": "Unknown destination test"
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        with open(LOG_FILE, "a", encoding="utf-8"):
            pass

        sock.sendto(
            encode_packet(packet),
            (r1["ip"], r1["port"])
        )

        print("Unknown-destination packet sent to R1.")
        print("Destination:", packet["destination"])

        time.sleep(1)

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()

        matching_lines = [
            line for line in lines if message_id in line
        ]

        drop_found = any(
            "DROP" in line
            for line in matching_lines
        )

        if drop_found:
            print("\nPASS: Router dropped the unknown destination packet.")
            for line in matching_lines:
                print(line.strip())
        else:
            print("\nFAIL: No DROP event found.")
            for line in matching_lines:
                print(line.strip())

    finally:
        sock.close()


if __name__ == "__main__":
    run_test()
