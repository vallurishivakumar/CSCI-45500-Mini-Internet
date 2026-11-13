# CSCI 4/5500: Computer Networks Mini Internet Project

## Fall 2026

### Team Members

- Darcy Mupenda
- Nayira Nwikpuinee
- Fnu Valluri Shiva Kumar

## Project Description

This project implements a mini-internet using Python 3 and UDP sockets. It contains two hosts and four routers that communicate using virtual addresses, packet formats, and static forwarding tables.

The main objective is to demonstrate communication between hosts through multiple routers. The project includes packet forwarding, packet validation, hop-limit handling, network delay and packet-loss simulation, and a reliable data transfer extension.

## Network Topology

The network contains six nodes:

- H1: Host 1
- H2: Host 2
- R1, R2, R3, and R4: Routers

The network supports two main communication paths:

**Lower route:** H1 → R1 → R3 → R4 → H2

**Upper route:** H1 → R1 → R2 → R4 → H2

Both forwarding paths were tested. The reverse communication path was also verified.

All nodes use UDP sockets on the local machine with the configured ports defined in `config/topology.json`.

## Project Implementation

The project includes:

- UDP-based communication between hosts and routers.
- Virtual network addresses and packet encoding and decoding.
- Static forwarding tables.
- Multi-hop communication between H1 and H2.
- PROBE and ECHO messages for basic connectivity testing.
- DATA and ACK messages for reliable transfer.
- Packet validation and malformed-packet handling.
- Hop-limit checking to prevent indefinite forwarding.
- Packet-size validation with a maximum packet size of 1200 bytes.
- Handling of unknown destinations and unavailable forwarding routes.
- Network packet-loss and delay simulation.
- Event logging to record network activity.

## Packet Format

Packets are encoded as JSON and transmitted as UTF-8 UDP datagrams.

The packet structure contains the following fields:

| Field | Description |
|---|---|
| source | Virtual source node |
| destination | Virtual destination node |
| hop_limit | Maximum remaining forwarding hops |
| message_type | PROBE, ECHO, DATA, or ACK |
| message_id | Identifier used to match messages and responses |
| payload | Message content |

The packet decoder validates the received packet structure and rejects malformed packets. The implementation also enforces a maximum packet size of 1200 bytes.

## Network Configuration and Simulation

The network topology and simulation settings are stored in:

`config/topology.json`

The configuration defines the nodes, UDP ports, neighbors, and static forwarding information.

The network simulation supports two settings:

- `packet_loss_percent`: Configured random packet-loss percentage.
- `delay_ms`: Configured forwarding delay in milliseconds.

The current implementation reads these settings globally at each router. Random packet loss is simulated using Python's random-number generator. Configured delay is applied using a blocking sleep operation before forwarding.

These settings are not independently configurable for individual links. Random seeds are not currently recorded, so exact repetition of random-loss experiments is not guaranteed.

## Reliable Transfer Extension: Track B

The project implements a Stop-and-Wait reliable transfer approach.

The sender transmits DATA packets and waits for matching ACK messages before proceeding to the next message.

The implementation includes:

- DATA packets and acknowledgment messages.
- Message identifiers for tracking packets.
- Acknowledgment timeouts.
- Retransmissions when acknowledgments are not received.
- Duplicate DATA message detection at the receiver.
- A maximum retry limit to prevent unlimited retransmissions.
- Sequential message transmission.

The reliable transfer was tested in both directions between H1 and H2.

The sender uses message identifiers 3001 through 3020 for a 20-message transfer. The receiver uses processed message identifiers to detect previously processed DATA messages and sends acknowledgments.

The available tests demonstrate successful transfers and recovery from some randomly dropped packets. However, separate deliberate DATA-drop and final ACK-drop tests have not been demonstrated. The receiver also does not implement the required bounded post-transfer acknowledgment grace period. Therefore, the complete Track B acceptance requirements have not yet been verified.

## Testing and Experiment Results

The project was tested using different packet-loss and delay configurations.

### Results at 0 ms Delay

Three runs were recorded for each transfer method under the 0% and 5% configured packet-loss conditions.

| Test condition | Best-effort | Reliable UDP |
|---|---:|---:|
| 0% packet loss | 60/60 (100%) | 60/60 (100%) |
| 5% packet loss | 38/60 (63.33%) | 60/60 (100%) |

At 5% configured packet loss, reliable UDP used 14 retransmissions across three runs and acknowledged all 60 DATA packets.

### Preliminary Results at 50 ms Delay

Additional single-run tests were recorded under 50 ms configured delay and 5% configured packet loss.

| Measurement | Best-effort | Reliable UDP |
|---|---:|---:|
| Packets attempted | 20 | 20 |
| Successful responses/ACKs | 14 | 20 |
| Failed/timeouts | 6 | 0 |
| Success rate | 70% | 100% |
| Retransmissions | 0 | 6 |

These results are preliminary and represent one recorded run for each method.

The complete repeated experiment matrix at 50 ms delay has not been completed. The current results also do not include recorded random seeds, RTT measurements, or RTT mean and spread.

The best-effort and reliable tests use different message types: PROBE/ECHO and DATA/ACK. Therefore, the results are an observed comparison rather than a fully controlled performance evaluation.

### Additional Tests

Additional tests included:

- Communication through both routing paths.
- Communication from H2 to H1.
- Hop-limit exhaustion and packet dropping.
- Malformed packet rejection.
- Oversized packet rejection.
- Unknown destination handling.
- Bounded retransmission when the destination host was not listening.
- Reliable transfer under configured packet loss and delay.

Detailed experiment summaries are available in `experiments/experiment_results.txt`.

## Evidence and Wireshark

The `evidence/` directory contains saved test outputs, configurations, logs, and packet-capture files.

Important evidence files include:

| File | Purpose |
|---|---|
| `routing_tests.txt` | Upper and lower routing test results |
| `forwarding_loop_test.txt` | Forwarding loop and hop-limit test evidence |
| `hop_limit_test.txt` | Hop-limit test output |
| `reliable_baseline_h1_h2.txt` | Reliable baseline test |
| `reliable_5loss_50ms.txt` | Reliable transfer under 5% loss and 50 ms delay |
| `best_effort_5loss_50ms.txt` | Best-effort transfer under the same settings |
| `delay_50ms_log.txt` | Simulated delay log evidence |
| `loss_5percent_50ms_log.txt` | Packet-loss log evidence |
| `topology.json` | Saved topology configuration |
| `topology_before_loop_test.json` | Topology before the forwarding-loop test |
| `network.log` | Recorded network events |
| `mini_internet_udp_capture.pcapng` | Wireshark UDP packet capture |
| `wireshark_reliable_data_ack.png` | Wireshark screenshot |

The Wireshark capture contains UDP traffic for the reliable transfer. The packet payloads show DATA and ACK messages with their virtual source and destination addresses.

The network log provides additional evidence of the multi-hop request and response paths. Together, the capture and logs help verify the packet exchange between H1 and H2 through the routers.

## Team Responsibilities

The initial project responsibilities were divided as follows:

- **Darcy Mupenda:** Router setup, neighbor connections, and static forwarding tables.
- **Nayira Nwikpuinee:** Packet format, virtual addresses, configuration, and packet parsing.
- **Fnu Valluri Shiva Kumar:** Host programs, UDP communication, and PROBE/ECHO messages.

All team members participated in testing, debugging, integration, and documentation.

## Project Structure

- `src/` - Python source files for hosts, routers, packet handling, logging, and tests.
- `config/` - Network topology and configuration.
- `logs/` - Network activity logs.
- `evidence/` - Test outputs, saved configurations, logs, and Wireshark evidence.
- `experiments/` - Experiment summaries and comparisons.
- `captures/` - Capture-related project directory.
- `check_config.py` - Configuration validation.
- `README.md` - Project documentation.

## Environment and Setup

The project was tested with:

- Python 3.11.9
- Python standard library
- UDP sockets
- PowerShell on Windows

No third-party Python packages are required by the current implementation.

### 1. Clone the Repository

```powershell
git clone https://github.com/vallurishivakumar/CSCI-45500-Mini-Internet.git
cd CSCI-45500-Mini-Internet
```

### 2. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Validate the Configuration

```powershell
python check_config.py
```

### 4. Verify Python Source Compilation

```powershell
python -m compileall src
```

## Running the Project

Run all commands from the main project directory. Open separate PowerShell terminals for the routers and hosts.

### 1. Start the Routers

Start each router in a separate terminal:

```powershell
python src/router.py R1
```

```powershell
python src/router.py R2
```

```powershell
python src/router.py R3
```

```powershell
python src/router.py R4
```

Keep all four router terminals running.

### 2. Start the Destination Host

Open another terminal:

```powershell
python src/host.py H2 --listen
```

Keep H2 running so it can receive packets and send responses.

### 3. Test Basic Connectivity

Open another terminal:

```powershell
python src/host.py H1 H2
```

### 4. Test Reliable UDP Transfer

Run a 20-message reliable transfer from H1 to H2:

```powershell
python src/host.py H1 H2 --reliable --count 20
```

To test the reverse direction:

```powershell
python src/host.py H2 H1 --reliable --count 20
```

### 5. Run the Test Programs

Execute the test programs individually:

```powershell
python src/test_network.py
python src/test_hop_limit.py
python src/test_invalid_packet.py
python src/test_oversized_packet.py
python src/test_unknown_destination.py
```

### 6. Stop the Processes

After completing the tests, stop the running routers and host processes by pressing `Ctrl+C` in their respective terminals.

## Known Limitations

The current implementation has the following limitations:

- Packet loss and delay settings apply globally at routers rather than to selected individual links.
- Random seeds are not recorded.
- Delay uses a blocking sleep operation and may temporarily prevent a router from handling other packets.
- The complete repeated experiment matrix at 50 ms delay has not been completed.
- RTT measurements, RTT mean and spread, elapsed time, throughput, and controlled sending rate were not measured.
- Best-effort PROBE/ECHO and reliable DATA/ACK tests use different packet types.
- Deliberate dropping of a specific DATA packet and final ACK packet has not been tested separately.
- The receiver does not implement a bounded post-transfer acknowledgment grace period.
- The bounded retry test demonstrated failure when the destination host was not listening, rather than when a forwarding route was missing.

These limitations should be considered when interpreting the experiment results and evaluating the reliable transfer extension.

## Repository Information

**GitHub repository:**

https://github.com/vallurishivakumar/CSCI-45500-Mini-Internet

**Audited commit:** `1680aee` — updated README file.

The local `main` branch was verified to match `origin/main` at this commit during the project audit.

## Conclusion

The project demonstrates multi-hop communication using UDP sockets, virtual network addresses, and static forwarding tables. Both forwarding paths were tested, and communication was verified in both directions.

The reliable transfer extension demonstrates acknowledgments, timeouts, retransmissions, and duplicate detection. The recorded experiments show 100% acknowledgment success for reliable UDP under the tested 5% packet-loss conditions, while best-effort communication achieved 63.33% success at 0 ms configured delay.

The project also includes packet validation, hop-limit protection, network simulation, logging, and Wireshark evidence. The remaining experimental and Track B limitations are documented to provide an accurate account of the implementation and its evaluation.