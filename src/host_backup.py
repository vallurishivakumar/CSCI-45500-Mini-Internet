
import argparse
import json
import socket
from pathlib import Path

from packet import create_packet, encode_packet, decode_packet
from logger import log_event


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_host(host_name, destination, payload):
    config = load_config()
    nodes = config["nodes"]

    if host_name not in nodes or nodes[host_name]["type"] != "host":
        raise ValueError(f"Unknown host: {host_name}")

    if destination not in nodes:
        raise ValueError(f"Unknown destination: {destination}")

    host = nodes[host_name]
    neighbor_name = host["neighbors"][0]
    neighbor = nodes[neighbor_name]

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

    data = encode_packet(packet)

    print(f"{host_name} is running at {host['ip']}:{host['port']}")
    print(f"Sending PROBE to {destination} through {neighbor_name}")

    sock.sendto(data, (neighbor["ip"], neighbor["port"]))

    log_event(
        event="SEND",
        node=host_name,
        message_id=packet["message_id"],
        message_type=packet["message_type"],
        source=packet["source"],
        destination=packet["destination"],
        next_hop=neighbor_name,
        hop_limit=packet["hop_limit"],
        details="PROBE packet sent",
    )

    try:
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
            message_type=response["message_type"],
            source=response["source"],
            destination=response["destination"],
            details="Echo response received",
        )

    except socket.timeout:
        print("\nNo response received within 5 seconds.")

        log_event(
            event="TIMEOUT",
            node=host_name,
            message_id=packet["message_id"],
            message_type=packet["message_type"],
            source=packet["source"],
            destination=packet["destination"],
            details="Response timeout after 5 seconds",
        )

    finally:
        sock.close()


def listen_as_host(host_name):
    config = load_config()
    nodes = config["nodes"]

    if host_name not in nodes or nodes[host_name]["type"] != "host":
        raise ValueError(f"Unknown host: {host_name}")

    host = nodes[host_name]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host["ip"], host["port"]))

    print(f"{host_name} is listening on {host['ip']}:{host['port']}")

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

            if (
                packet["destination"] != host_name
                or packet["message_type"] != "PROBE"
            ):
                log_event(
                    event="DROP",
                    node=host_name,
                    message_id=packet["message_id"],
                    details="Packet is not a PROBE for this host",
                )
                continue

            response = create_packet(
                source=host_name,
                destination=packet["source"],
                hop_limit=10,
                message_type="ECHO",
                message_id=packet["message_id"],
                payload=packet["payload"],
            )

            sock.sendto(encode_packet(response), sender)

            log_event(
                event="SEND",
                node=host_name,
                message_id=response["message_id"],
                message_type=response["message_type"],
                source=response["source"],
                destination=response["destination"],
                next_hop=str(sender),
                hop_limit=response["hop_limit"],
                details="Echo response sent",
            )

    except KeyboardInterrupt:
        print(f"\n{host_name} stopped.")

    finally:
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default="H1")
    parser.add_argument("destination", nargs="?", default="H2")
    parser.add_argument("--message", default="Hello from H1")
    parser.add_argument(
        "--listen",
        action="store_true",
        help="Listen for incoming PROBE packets and send ECHO responses",
    )

    args = parser.parse_args()

    if args.listen:
        listen_as_host(args.host)
    else:
        run_host(args.host, args.destination, args.message)
