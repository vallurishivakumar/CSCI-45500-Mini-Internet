
import csv
import os
from datetime import datetime


LOG_DIRECTORY = "logs"
LOG_FILE = os.path.join(LOG_DIRECTORY, "network.log")
CSV_FILE = os.path.join(LOG_DIRECTORY, "network.csv")


def log_event(
    event,
    node="UNKNOWN",
    message_id="",
    message_type="",
    source="",
    destination="",
    next_hop="",
    hop_limit="",
    details="",
):
    """Record a network event in both text and CSV log files."""

    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="milliseconds")

    log_entry = (
        f"{timestamp} | {event} | Node={node} | "
        f"MessageID={message_id} | Type={message_type} | "
        f"Source={source} | Destination={destination} | "
        f"NextHop={next_hop} | HopLimit={hop_limit} | "
        f"Details={details}"
    )

    print(log_entry)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry + "\n")

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "event",
                "node",
                "message_id",
                "message_type",
                "source",
                "destination",
                "next_hop",
                "hop_limit",
                "details",
            ])

        writer.writerow([
            timestamp,
            event,
            node,
            message_id,
            message_type,
            source,
            destination,
            next_hop,
            hop_limit,
            details,
        ])


if __name__ == "__main__":
    print("Testing network logger...")

    log_event(
        event="SEND",
        node="H1",
        message_id="1001",
        message_type="PROBE",
        source="H1",
        destination="H2",
        next_hop="R1",
        hop_limit=10,
        details="Test packet sent",
    )

    print("Logger test completed!")
