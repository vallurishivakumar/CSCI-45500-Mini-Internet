
import argparse
import json
import socket
import time
from pathlib import Path

from packet import create_packet, encode_packet, decode_packet
from logger import log_event


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_host_details(host_name, destination):
    config = load_config()
    nodes = config["nodes"]

    if host_name not in nodes or nodes[host_name]["type"] != "host":
        raise ValueError(f"Unknown host: {host_name}")

    if destination not in nodes or nodes[destination]["type"] != "host":
        raise ValueError(f"Unknown destination host: {destination}")

    host = nodes[host_name]
    neighbor_name = host["neighbors"][0]
    neighbor = nodes[neighbor_name]

    return host, neighbor, neighbor_name


# --------------------------------------------------
# ORIGINAL BEST-EFFORT UDP COMMUNICATION
# --------------------------------------------------

def run_host(host_name, destination, payload):
    host, neighbor, neighbor_name = get_host_details(
        host_name, destination
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host["ip"], host["port"]))
    sock.settimeout(5)

    packet = create_packet(
        source=host_name,
        destination=destination,
        hop_limit=10,
        message_type="PROBE",
        message_id="1001",
        payload=payload,
    )

    print(f"{host_name} is running at {host['ip']}:{host['port']}")
    print(f"Sending PROBE to {destination} through {neighbor_name}")

    try:
        sock.sendto(
            encode_packet(packet),
            (neighbor["ip"], neighbor["port"])
        )

        log_event(
            event="SEND",
            node=host_name,
            message_id=packet["message_id"],
            message_type="PROBE",
            source=host_name,
            destination=destination,
            next_hop=neighbor_name,
            hop_limit=10,
            details="PROBE packet sent",
        )

        response_data, sender = sock.recvfrom(4096)
        response = decode_packet(response_data)

        if (
            response["message_type"] != "ECHO"
            or response["message_id"] != packet["message_id"]
            or response["source"] != destination
            or response["destination"] != host_name
        ):
            print("Received an unexpected response.")
            return

        print("\nResponse received successfully!")
        print("Response packet:", response)
        print("Received from:", sender)

        log_event(
            event="RECEIVE",
            node=host_name,
            message_id=response["message_id"],
            message_type="ECHO",
            source=destination,
            destination=host_name,
            details="Echo response received",
        )

    except socket.timeout:
        print("\nNo response received within 5 seconds.")

        log_event(
            event="TIMEOUT",
            node=host_name,
            message_id=packet["message_id"],
            message_type="PROBE",
            source=host_name,
            destination=destination,
            details="Response timeout after 5 seconds",
        )

    finally:
        sock.close()


# --------------------------------------------------
# RELIABLE UDP SENDER: STOP-AND-WAIT
# --------------------------------------------------

def run_reliable_host(
    host_name,
    destination,
    payload,
    count,
    retries,
    timeout
):
    host, neighbor, neighbor_name = get_host_details(
        host_name, destination
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host["ip"], host["port"]))

    successful = 0
    failed = 0
    total_retransmissions = 0

    print("\n" + "=" * 55)
    print("RELIABLE UDP TRANSFER - STOP-AND-WAIT")
    print("=" * 55)
    print(f"Source: {host_name}")
    print(f"Destination: {destination}")
    print(f"Packets: {count}")
    print(f"Maximum retransmissions per packet: {retries}")
    print(f"ACK timeout: {timeout} seconds")
    print("=" * 55)

    try:
        for sequence in range(1, count + 1):

            message_id = str(3000 + sequence)
            packet_payload = f"{payload} - Sequence {sequence}"

            packet = create_packet(
                source=host_name,
                destination=destination,
                hop_limit=10,
                message_type="DATA",
                message_id=message_id,
                payload=packet_payload,
            )

            encoded_packet = encode_packet(packet)
            acknowledged = False

            for attempt in range(1, retries + 2):

                if attempt > 1:
                    total_retransmissions += 1
                    print(
                        f"Packet {sequence}: "
                        f"RETRANSMISSION {attempt - 1}"
                    )

                sock.sendto(
                    encoded_packet,
                    (neighbor["ip"], neighbor["port"])
                )

                log_event(
                    event="SEND",
                    node=host_name,
                    message_id=message_id,
                    message_type="DATA",
                    source=host_name,
                    destination=destination,
                    next_hop=neighbor_name,
                    hop_limit=10,
                    details=f"Sequence {sequence}, attempt {attempt}",
                )

                print(
                    f"\nPacket {sequence}/{count}: "
                    f"DATA sent (attempt {attempt})"
                )

                deadline = time.monotonic() + timeout

                while True:
                    remaining = deadline - time.monotonic()

                    if remaining <= 0:
                        break

                    sock.settimeout(remaining)

                    try:
                        response_data, sender = sock.recvfrom(4096)
                        response = decode_packet(response_data)

                    except socket.timeout:
                        break

                    except ValueError:
                        continue

                    # Accept only the matching ACK.
                    if (
                        response["message_type"] == "ACK"
                        and response["message_id"] == message_id
                        and response["source"] == destination
                        and response["destination"] == host_name
                    ):
                        acknowledged = True
                        successful += 1

                        print(
                            f"Packet {sequence}: ACK received "
                            f"from {destination}"
                        )

                        log_event(
                            event="RECEIVE",
                            node=host_name,
                            message_id=message_id,
                            message_type="ACK",
                            source=destination,
                            destination=host_name,
                            details=f"Sequence {sequence} acknowledged",
                        )

                        break

                if acknowledged:
                    break

                print(
                    f"Packet {sequence}: ACK timeout "
                    f"after {timeout} seconds"
                )

                log_event(
                    event="TIMEOUT",
                    node=host_name,
                    message_id=message_id,
                    message_type="DATA",
                    source=host_name,
                    destination=destination,
                    details=f"Attempt {attempt} timed out",
                )

            if not acknowledged:
                failed += 1
                print(
                    f"Packet {sequence}: FAILED after "
                    f"{retries + 1} attempts"
                )

    except KeyboardInterrupt:
        print("\nReliable transfer interrupted.")

    finally:
        sock.close()

    total = successful + failed

    print("\n" + "=" * 55)
    print("RELIABLE UDP RESULTS")
    print("=" * 55)
    print(f"Total packets attempted: {total}")
    print(f"Successfully acknowledged: {successful}")
    print(f"Failed packets: {failed}")
    print(f"Retransmissions: {total_retransmissions}")

    if total > 0:
        print(f"Success rate: {successful / total * 100:.2f}%")

    print("=" * 55)


# --------------------------------------------------
# HOST RECEIVER: H2
# --------------------------------------------------


def listen_as_host(host_name):
    config = load_config()
    nodes = config["nodes"]

    if host_name not in nodes or nodes[host_name]["type"] != "host":
        raise ValueError(f"Unknown host: {host_name}")

    host = nodes[host_name]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host["ip"], host["port"]))

    # Store message IDs that have already been processed.
    processed_data_ids = set()

    print(
        f"{host_name} is listening on "
        f"{host['ip']}:{host['port']}"
    )

    try:
        while True:
            data, sender = sock.recvfrom(4096)

            try:
                packet = decode_packet(data)

            except ValueError as error:
                log_event(
                    event="DROP",
                    node=host_name,
                    details=f"Invalid packet: {error}",
                )
                continue

            log_event(
                event="RECEIVE",
                node=host_name,
                message_id=packet["message_id"],
                message_type=packet["message_type"],
                source=packet["source"],
                destination=packet["destination"],
                details=f"Received from UDP {sender}",
            )

            if packet["destination"] != host_name:
                log_event(
                    event="DROP",
                    node=host_name,
                    message_id=packet["message_id"],
                    details="Packet has incorrect destination",
                )
                continue

            # Original best-effort PROBE handling.
            if packet["message_type"] == "PROBE":

                response_type = "ECHO"
                response_payload = packet["payload"]

            # Reliable DATA handling with duplicate detection.
            elif packet["message_type"] == "DATA":

                message_id = packet["message_id"]

                response_type = "ACK"
                response_payload = "ACK"

                if message_id in processed_data_ids:

                    print(
                        f"DUPLICATE DATA detected: "
                        f"Sequence {message_id}"
                    )

                    print(
                        f"Sending ACK again for duplicate "
                        f"message {message_id}"
                    )

                else:

                    # Remember this message so it is not
                    # processed again if retransmitted.
                    processed_data_ids.add(message_id)

                    print(
                        f"NEW DATA received and processed: "
                        f"Sequence {message_id}"
                    )

            else:
                log_event(
                    event="DROP",
                    node=host_name,
                    message_id=packet["message_id"],
                    details="Unsupported message type",
                )
                continue

            # Send ECHO or ACK response.
            response = create_packet(
                source=host_name,
                destination=packet["source"],
                hop_limit=10,
                message_type=response_type,
                message_id=packet["message_id"],
                payload=response_payload,
            )

            sock.sendto(
                encode_packet(response),
                sender
            )

            print(
                f"{response_type} sent for "
                f"message {packet['message_id']}"
            )

            log_event(
                event="SEND",
                node=host_name,
                message_id=response["message_id"],
                message_type=response_type,
                source=host_name,
                destination=packet["source"],
                next_hop=str(sender),
                hop_limit=10,
                details=f"{response_type} response sent",
            )

    except KeyboardInterrupt:
        print(f"\n{host_name} stopped.")

    finally:
        sock.close()



# --------------------------------------------------
# COMMAND-LINE OPTIONS
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("host", nargs="?", default="H1")
    parser.add_argument("destination", nargs="?", default="H2")

    parser.add_argument(
        "--message",
        default="Hello from H1"
    )

    parser.add_argument(
        "--listen",
        action="store_true",
        help="Listen for incoming packets"
    )

    parser.add_argument(
        "--reliable",
        action="store_true",
        help="Use reliable Stop-and-Wait UDP transfer"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=20
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=5
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=1.5
    )

    args = parser.parse_args()

    if args.count < 1 or args.retries < 0 or args.timeout <= 0:
        parser.error("Count and timeout must be positive; retries cannot be negative.")

    if args.listen:
        listen_as_host(args.host)

    elif args.reliable:
        run_reliable_host(
            args.host,
            args.destination,
            args.message,
            args.count,
            args.retries,
            args.timeout,
        )

    else:
        run_host(
            args.host,
            args.destination,
            args.message
        )
