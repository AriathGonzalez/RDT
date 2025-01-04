# Reliable Data Transfer (RDT) Simulation

A simulation of Reliable Data Transfer (RDT) protocols, implementing **Stop-and-Wait (SNW)** and **Go-Back-N (GBN)** to ensure reliable communication over an unreliable network channel.

---

## Features

- **Stop-and-Wait ARQ:** Reliable communication using alternating sequence numbers.
- **Go-Back-N ARQ:** Optimized sliding window protocol for increased efficiency.
- **Error Detection and Recovery:** Utilizes checksums, sequence numbers, and ACK/NAK mechanisms.
- **Timeout Management:** Handles retransmissions via a simple timer.
- **File Transfer Simulation:** Demonstrates reliable file uploads from client to server.

---

## Technologies Used

- **Programming Language:** Python
- **Networking Protocols:** UDP for unreliable data transfer simulation
- **Tools and Concepts:** Sequence Numbers, Checksum, Timers, Sliding Window

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rdt-simulation.git
   cd rdt-simulation
   ```
   
2. Ensure Python 3.x is installed on your system.

3. Configure the following parameters in client.py and server.py:
  - HOST (Server IP Address)
  - port (Server Port)
  - MSS (Maximum Segment Size)

## Usage
1. Start the server
   ```bash
   python server.py -p port -r protocol -n window_size
   ```
2. Start the client
   ```bash
   python client.py -p port -r protocol -f file -n window_size
   ```
