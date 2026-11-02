
import json


MAX_PACKET_SIZE = 1200

REQUIRED_FIELDS = {
    "source",
    "destination",
    "hop_limit",
    "message_type",
    "message_id",
    "payload",
}

ALLOWED_MESSAGE_TYPES = {
    "PROBE",
    "ECHO",
    "DATA",
    "ACK",
}


def create_packet(source, destination, hop_limit, message_type, message_id, payload):
    """Create a packet using the project's standard fields."""

    packet = {
        "source": source,
        "destination": destination,
        "hop_limit": hop_limit,
        "message_type": message_type,
        "message_id": str(message_id),
        "payload": payload,
    }

    validate_packet(packet)
    return packet


def validate_packet(packet):
    """Check that a packet has all required fields and valid values."""

    if not isinstance(packet, dict):
        raise ValueError("Packet must be a dictionary")

    if set(packet.keys()) != REQUIRED_FIELDS:
        raise ValueError("Packet has missing or unexpected fields")

    if not isinstance(packet["source"], str) or not packet["source"]:
        raise ValueError("Source must be a non-empty string")

    if not isinstance(packet["destination"], str) or not packet["destination"]:
        raise ValueError("Destination must be a non-empty string")

    if (
        not isinstance(packet["hop_limit"], int)
        or isinstance(packet["hop_limit"], bool)
        or not 1 <= packet["hop_limit"] <= 255
    ):
        raise ValueError("Hop limit must be an integer from 1 to 255")

    if packet["message_type"] not in ALLOWED_MESSAGE_TYPES:
        raise ValueError("Invalid message type")

    if not isinstance(packet["message_id"], str) or not packet["message_id"]:
        raise ValueError("Message ID must be a non-empty string")

    if not isinstance(packet["payload"], str):
        raise ValueError("Payload must be a string")

    return True


def encode_packet(packet):
    """Convert a packet dictionary into UDP-ready bytes."""

    validate_packet(packet)

    encoded = json.dumps(packet).encode("utf-8")

    if len(encoded) > MAX_PACKET_SIZE:
        raise ValueError("Packet exceeds the 1200-byte limit")

    return encoded


def decode_packet(data):
    """Convert received UDP bytes into a validated packet."""

    if not isinstance(data, bytes):
        raise ValueError("Received packet must be bytes")

    if len(data) > MAX_PACKET_SIZE:
        raise ValueError("Received packet exceeds the 1200-byte limit")

    try:
        packet_text = data.decode("utf-8")
        packet = json.loads(packet_text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Packet is not valid UTF-8 JSON")

    validate_packet(packet)
    return packet


if __name__ == "__main__":
    print("Testing packet module...")

    test_packet = create_packet(
        source="H1",
        destination="H2",
        hop_limit=10,
        message_type="PROBE",
        message_id="1001",
        payload="Hello from H1",
    )

    encoded = encode_packet(test_packet)
    decoded = decode_packet(encoded)

    print("Original packet:", test_packet)
    print("Encoded size:", len(encoded), "bytes")
    print("Decoded packet:", decoded)

    assert decoded == test_packet

    print("Packet module test passed!")
