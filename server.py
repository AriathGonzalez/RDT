'''
Ingredients for RDT:
- ACK/NAK
- Checksum
- Sequence #
- Timer 

Experimental Setup: Client is seeking to upload file to server,
    meaning:
    1) client implements sender's logic
    2) server implements receiver's logic

This is the receiver program, this will be started first.

Stop-and-Wait ARQ:
- Wait for data to arrive
    - Checksum(): data and sequence valid
        - Send ACK
    - else: send NAK
Note: Timer would be for sender side.
'''
import socket
import sys
import udt, packet


# Constants
HOST = "127.0.0.1"
CACHE = "ServerCache/"
MSS = 1000


class ClientState:
    """
    Represents the state of a client.

    Attributes:
        rcv_base (int): The expected sequence number for the next packet to be received.
        max_packets (int): The maximum number of packets transmitted by the client.
    """

    def __init__(self, initial_seq, max_packets):
        """
        Initializes a ClientState object.

        Parameters:
            initial_seq (int): The initial sequence number for the client.
            max_packets (int): The maximum number of packets transmitted by the client.
        """
        self.rcv_base = initial_seq
        self.max_packets = max_packets


def create_checksum(i, data):
    """
    Creates a checksum for the given data.

    Parameters:
        i (int): Sequence number.
        data (bytes): Data for which checksum is to be created.

    Returns:
        str: Computed checksum.
    """

    # Add sequence number
    data = bytes([i]) + data

    # Get sum of bits
    data_sum = len(data)
    bit_sum = bin(data_sum)[2:]

    # Pad to 10 bits
    while len(bit_sum) < 10: 
        bit_sum = '0' + bit_sum

    # Get Ones' Complement (Flip all the bits)
    checksum = ''
    for bit in bit_sum:
        checksum += '1' if bit == '0' else '0'

    return checksum


def verify_checksum(i, checksum, data):
    """
    Verifies the checksum of the received data.

    Parameters:
        i (int): Sequence number.
        checksum (str): Received checksum.
        data (bytes): Received data.

    Returns:
        bool: True if the checksum is valid, False otherwise.
    """
    if checksum == b"DONE" or checksum == b"FIRST":
        return True

    received_checksum = create_checksum(i, data).encode("utf-8")

    return checksum == received_checksum


def main():
    """
    Main function to start the server.
    """
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = (HOST, port)
    sock.bind(server_address)

    clients = {}   # Store the states for multiple clients
    while True:
        pkt, addr = udt.recv(sock)
        seq, checksum, data_rcvd = packet.extract(pkt)

        if verify_checksum(seq, checksum, data_rcvd):
            # End: close socket if "DONE" packet received
            if checksum == b"DONE":
                del clients[addr]
                sock.close()
                break
            
            # First: receive file extension to deliver following packets
            if checksum == b"FIRST":
                data_str = data_rcvd.decode("utf-8")
                extension, max_packets_transmitted = data_str.split(":")
                clients[addr] = ClientState(1, int(max_packets_transmitted))  # (current packet, max packets)

            # Deliver the data
            if checksum != b"FIRST" and (clients[addr].rcv_base % clients[addr].max_packets) == (seq % clients[addr].max_packets):
                clients[addr].rcv_base += 1  # Update expected sequence number
                output_file = f"{CACHE}{addr[0]}_{addr[1]}.{extension}"
                with open(output_file, 'ab') as file:
                    file.write(data_rcvd)

            # Send acknowledgement
            ack_to_send = "ACK - " + str(seq % clients[addr].max_packets)
            ackpkt = packet.make(clients[addr].rcv_base % clients[addr].max_packets, create_checksum(clients[addr].rcv_base % clients[addr].max_packets , bytes(ack_to_send, "utf-8")).encode("utf-8"), bytes(ack_to_send, "utf-8"))
            udt.send(ackpkt, sock, addr)
            print("Server: Ack sent - %s", ack_to_send)
    
    
if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) < 7:
        print('Usage : "python server.py -p port -r protocol -n window_size (0 - SnW, 1 - GBN)"\n[port: port number that server will bind and listen on]\n[protocol: protocol the server will use (SnW or GBN)]\n[window_size: window size used by the sender/receiver in GBN]')
        sys.exit(2)
    
    # Parse command-line arguments
    args = {}
    for flag, value in zip(sys.argv[1::2], sys.argv[2::2]):
        args[flag] = value
    
    if '-p' not in args or '-r' not in args or '-n' not in args:
        print("Error: Missing required options.")
        sys.exit(2)
    
    # Variables we need
    port = int(args['-p'])
    protocol = int(args['-r'])
    window_size = int(args['-n'])

    # Start the server
    main()
