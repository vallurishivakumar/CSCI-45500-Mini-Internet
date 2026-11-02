
import json
import socket
from pathlib import Path

from packet import encode_packet, decode_packet


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"

TOTAL_PROBES = 20
TIMEOUT_SECONDS = 3


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_tests():
    config = load_config()
    nodes = config["nodes"]

    h1 = nodes["H1"]
    r1_name = h1["neighbors"][0]
    r1 = nodes[r1_name]

    successful = 0
    failed = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((h1["ip"], h1["port"]))
    sock.settimeout(TIMEOUT_SECONDS)

    print("=" * 50)
    print("MINI INTERNET - 20 PROBE NETWORK TEST")
    print("=" * 50)

    try:
        for number in range(1, TOTAL_PROBES + 1):
            message_id = str(2000 + number)

            packet = {
                "source": "H1",
                "destination": "H2",
                "hop_limit": 10,
                "message_type": "PROBE",
                "message_id": message_id,
                "payload": f"Network test packet {number}"
            }

            try:
                outgoing_data = encode_packet(packet)

                sock.sendto(
                    outgoing_data,
                    (r1["ip"], r1["port"])
                )

                print(f"\nTest {number}/{TOTAL_PROBES}: PROBE sent")

                response_data, sender = sock.recvfrom(4096)
                response = decode_packet(response_data)

                if (
                    response["message_type"] == "ECHO"
                    and response["message_id"] == message_id
                    and response["source"] == "H2"
                    and response["destination"] == "H1"
                    and response["payload"] == packet["payload"]
                ):
                    successful += 1
                    print(f"Test {number}: SUCCESS - ECHO received")
                else:
                    failed += 1
                    print(f"Test {number}: FAILED - Invalid response")
                    print("Response:", response)

            except socket.timeout:
                failed += 1
                print(f"Test {number}: FAILED - Timeout")

            except (ValueError, OSError, KeyError) as error:
                failed += 1
                print(f"Test {number}: FAILED - {error}")

    finally:
        sock.close()

    success_rate = (successful / TOTAL_PROBES) * 100
    failure_rate = (failed / TOTAL_PROBES) * 100

    print("\n" + "=" * 50)
    print("NETWORK TEST RESULTS")
    print("=" * 50)
    print(f"Total probes:  {TOTAL_PROBES}")
    print(f"Successful:    {successful}")
    print(f"Failed:        {failed}")
    print(f"Success rate:  {success_rate:.2f}%")
    print(f"Failure rate:  {failure_rate:.2f}%")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
