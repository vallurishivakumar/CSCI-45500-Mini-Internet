
import argparse
import json
import random
import socket
import time
from pathlib import Path

from packet import decode_packet, encode_packet
from logger import log_event


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "topology.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_router(router_name):
    config = load_config()
    nodes = config["nodes"]
    forwarding = config["forwarding"]

    # Read network simulation settings.
    conditions = config.get("network_conditions", {})

    packet_loss = float(
        conditions.get("packet_loss_percent", 0)
    )
    delay_ms = float(
        conditions.get("delay_ms", 0)
    )

    if not 0 <= packet_loss <= 100:
        raise ValueError("Packet loss must be between 0 and 100.")

    if delay_ms < 0:
        raise ValueError("Delay cannot be negative.")

    if router_name not in nodes or nodes[router_name]["type"] != "router":
        raise ValueError(f"Unknown router: {router_name}")

    router = nodes[router_name]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((router["ip"], router["port"]))

    print(
        f"{router_name} is listening on "
        f"{router['ip']}:{router['port']}"
    )
    print(f"Neighbors: {router['neighbors']}")
    print(f"Packet loss: {packet_loss}%")
    print(f"Packet delay: {delay_ms} ms")

    try:
        while True:
            # Receive an incoming UDP packet.
            try:
                data, sender = sock.recvfrom(4096)

            except ConnectionResetError:
                log_event(
                    event="DROP",
                    node=router_name,
                    details="Windows reported that the UDP destination is unreachable",
                )
                continue

            # Decode and validate the packet.
            try:
                packet = decode_packet(data)

            except ValueError as error:
                log_event(
                    event="DROP",
                    node=router_name,
                    details=f"Invalid packet: {error}",
                )
                continue

            # Log packet reception.
            log_event(
                event="RECEIVE",
                node=router_name,
                message_id=packet["message_id"],
                message_type=packet["message_type"],
                source=packet["source"],
                destination=packet["destination"],
                hop_limit=packet["hop_limit"],
                details=f"Received from UDP {sender}",
            )

            # Simulate random packet loss.
            if random.random() < packet_loss / 100:
                log_event(
                    event="DROP",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    hop_limit=packet["hop_limit"],
                    details=f"Simulated packet loss ({packet_loss}%)",
                )
                continue

            # Check the hop limit.
            if packet["hop_limit"] <= 1:
                log_event(
                    event="DROP",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    hop_limit=packet["hop_limit"],
                    details="Hop limit exhausted",
                )
                continue

            # Find the next hop using the forwarding table.
            next_hop = forwarding[router_name].get(
                packet["destination"]
            )

            if next_hop is None:
                log_event(
                    event="DROP",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    hop_limit=packet["hop_limit"],
                    details="No forwarding route",
                )
                continue

            # Make sure the next hop is a direct neighbor.
            if next_hop not in router["neighbors"]:
                log_event(
                    event="DROP",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    details=f"{next_hop} is not a configured neighbor",
                )
                continue

            next_node = nodes[next_hop]

            # Simulate network delay.
            if delay_ms > 0:
                log_event(
                    event="DELAY",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    next_hop=next_hop,
                    details=f"Simulated delay of {delay_ms} ms",
                )

                time.sleep(delay_ms / 1000)

            # Decrease the hop limit before forwarding.
            packet["hop_limit"] -= 1

            # Forward the packet to the next node.
            try:
                outgoing_data = encode_packet(packet)

                sock.sendto(
                    outgoing_data,
                    (next_node["ip"], next_node["port"]),
                )

                log_event(
                    event="FORWARD",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    next_hop=next_hop,
                    hop_limit=packet["hop_limit"],
                    details="Packet forwarded successfully",
                )

            except (ValueError, OSError) as error:
                log_event(
                    event="DROP",
                    node=router_name,
                    message_id=packet["message_id"],
                    message_type=packet["message_type"],
                    source=packet["source"],
                    destination=packet["destination"],
                    next_hop=next_hop,
                    hop_limit=packet["hop_limit"],
                    details=f"Forwarding failed: {error}",
                )

    except KeyboardInterrupt:
        print(f"\n{router_name} stopped.")

    finally:
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "router",
        nargs="?",
        default="R1",
        help="Router name, for example R1 or R2",
    )

    args = parser.parse_args()

    run_router(args.router)
