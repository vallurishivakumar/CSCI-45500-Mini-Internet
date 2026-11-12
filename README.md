# CSCI 4/5500: Computer Networks Mini Internet Project

## Fall 2026

### Team Members

- Darcy Mupenda
- Nayira Nwikpuinee
- Fnu Valluri Shiva Kumar

## Project Description

This project implements a mini-internet using Python 3 and UDP sockets. It contains hosts and routers that communicate using virtual addresses, packet formats, and static forwarding tables.

The main objective is to demonstrate communication between hosts through multiple routers. The project also includes packet forwarding, packet validation, hop-limit handling, and reliable data transfer.

## Network Topology

The network contains two hosts and four routers:

- H1: Host 1
- H2: Host 2
- R1, R2, R3, and R4: Routers

The network uses the following main communication paths:

**Lower route:** H1 → R1 → R3 → R4 → H2

**Upper route:** H1 → R1 → R2 → R4 → H2

Both forwarding paths were tested successfully. The original lower route was restored after testing the alternate upper route.

## Project Implementation

The project includes the following features:

- UDP-based communication between hosts and routers.
- Virtual network addresses and packet encoding and decoding.
- Static forwarding tables for routing packets.
- Multi-hop communication between H1 and H2.
- PROBE and ECHO messages for basic connectivity testing.
- Packet validation and handling of malformed packets.
- Hop-limit checking to prevent packets from being forwarded indefinitely.
- Packet-size validation with a 1200-byte limit.
- Handling of unknown destinations when no forwarding route exists.

## Reliable Transfer Extension

The project implements Track B - Reliable Transfer using a Stop-and-Wait approach.

The reliable transfer functionality includes:

- DATA packets and acknowledgment (ACK) messages.
- Message identifiers for tracking packets.
- Acknowledgment timeouts.
- Retransmission when an acknowledgment is not received.
- Duplicate message detection at the receiver.
- A maximum retry limit to prevent unlimited retransmissions.

The reliable transfer was tested in both directions between H1 and H2.

## Testing and Experiment Results

The project was tested under 0% and 5% configured packet-loss conditions with 0 ms configured delay.

The main results were:

| Test condition | Best-effort | Reliable UDP |
|---|---:|---:|
| 0% packet loss | 60/60 (100%) | 60/60 (100%) |
| 5% packet loss | 38/60 (63.33%) | 60/60 (100%) |

At 5% configured packet loss, reliable UDP used 14 retransmissions across three runs and successfully acknowledged all 60 DATA packets.

Additional tests included:

- Successful communication through both routing paths.
- Communication from H2 to H1.
- Hop-limit exhaustion.
- Malformed packet handling.
- Oversized packet rejection.
- Unknown destination handling.
- Bounded retransmission when the destination host was not listening.

Detailed results are available in `experiments/experiment_results.txt`. Routing evidence is available in `evidence/routing_tests.txt`.

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
- `evidence/` - Routing test evidence and saved configurations.
- `experiments/` - Experiment results and comparisons.
- `README.md` - Project documentation.

## Running the Project

Use Python 3 and activate the project's virtual environment before running the programs. Open separate PowerShell terminals for the routers and hosts. Run all commands from the main project directory.

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

Keep all four router terminals running while performing network tests.

### 2. Start the Destination Host

Open another terminal and start H2 in listening mode:

```powershell
python src/host.py H2 --listen
```

Keep H2 running so it can receive packets from H1 and send responses.

### 3. Test Basic Connectivity

Open another terminal and run a basic connectivity test from H1 to H2:

```powershell
python src/host.py H1 H2
```

### 4. Test Reliable UDP Transfer

Run reliable transfer with 20 DATA packets:

```powershell
python src/host.py H1 H2 --reliable --count 20
```

The reverse-direction reliable transfer can be tested using:

```powershell
python src/host.py H2 H1 --reliable --count 20
```

### 5. Run the Test Programs

The following test programs can be executed individually to verify network functionality and packet handling:

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

The best-effort and reliable transfer experiments use different packet types: PROBE/ECHO and DATA/ACK. Therefore, the results are an observed comparison rather than a fully controlled performance evaluation.

Elapsed time, throughput, and sending rate were not measured. Deliberately dropping a specific DATA packet and a specific ACK packet was not tested separately. The bounded retry test demonstrated failure when the destination host was not listening, rather than when a forwarding route was missing.

## Conclusion

The project demonstrates multi-hop communication using UDP sockets, static routing, and virtual network addresses. Both forwarding paths were tested successfully, and communication was verified in both directions.

The reliable transfer extension demonstrated the use of acknowledgments, timeouts, retransmissions, and duplicate detection. The experiments showed that reliable UDP achieved 100% acknowledgment success under the tested 5% packet-loss condition, while best-effort communication delivered 63.33% of its probes.