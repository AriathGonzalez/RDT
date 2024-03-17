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


def create_checksum(i, data):
    """
    Creates a checksum for the given data.

    Parameters:
        i (int): Sequence number.
        data (bytes): Data for which checksum is to be created.

    Returns:
        str: Computed checksum.
    """
    data_sum = len(data)
    bit_sum = bin(data_sum)[2:]

    # Pad to 10 bits
    while len(bit_sum) < 10: 
        bit_sum = '0' + bit_sum

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

    data_sum = len(data)
    total_sum = data_sum + int(checksum, 2)
    total_sum_bits = bin(total_sum)[2:]
    for bit in total_sum_bits:
        if bit == '0':
            return False
    return True


def snw_receiver(sock):
    """
    Receives packets using Stop-and-Wait protocol.

    Parameters:
    - sock (socket.socket): The UDP socket to receive packets on.
    """
    expected_seq = 0
    while True:
        pkt, addr = udt.recv(sock)
        seq, checksum, data_rcvd = packet.extract(pkt)

        if verify_checksum(seq, checksum, data_rcvd):
            # TODO: Right now, Client doens't care about ack for last pkt or DONE
            # End: close socket if "DONE" packet received
            if checksum == b"DONE":
                sock.close()
                break
            
            # First: receive file extension to deliver following packets
            if checksum == b"FIRST":
                extension = data_rcvd.decode("utf-8")
                expected_seq = 1

            # Deliver the data
            if checksum != b"FIRST" and (expected_seq % 2) == (seq % 2):
                expected_seq += 1
                output_file = f"{CACHE}{addr[0]}_{addr[1]}.{extension}"
                with open(output_file, 'ab') as file:
                    file.write(data_rcvd)

            # Send acknowledgement
            ack_to_send = "ACK - " + str(seq % 2)
            ackpkt = packet.make(expected_seq % 2, create_checksum(expected_seq % 2 , ack_to_send).encode('utf-8'), bytes(ack_to_send, 'utf-8'))   # TODO: all seq here, were originally i
            udt.send(ackpkt, sock, addr)
            print("Server: Ack sent - %s", ack_to_send)


def gbn_receiver(sock):
    """
    Receives packets using Go-Back-N protocol.

    Parameters:
    - sock (socket.socket): The UDP socket to receive packets on.
    """
    rcv_base = 0
    while True:
        pkt, addr = udt.recv(sock)
        seq, checksum, data_rcvd = packet.extract(pkt)

        if verify_checksum(seq, checksum, data_rcvd):
            # TODO: Right now, Client doesn't care about ack for last pkt or DONE
            # End: close socket if "DONE" packet received
            if checksum == b"DONE":
                sock.close()
                break

            # First: receive file extension to deliver following packets
            if checksum == b"FIRST":
                extension = data_rcvd.decode("utf-8")
                rcv_base = 1

            # Deliver the data
            if checksum != b"FIRST" and rcv_base == seq: 
                rcv_base += 1
                output_file = f"{CACHE}{addr[0]}_{addr[1]}.{extension}"
                with open(output_file, "ab") as file:
                    file.write(data_rcvd)

            # Send acknowledgement
            ack_to_send = "ACK - " + str(seq)
            ackpkt = packet.make(rcv_base, create_checksum(rcv_base, ack_to_send).encode("utf-8"), bytes(ack_to_send, "utf-8"))
            udt.send(ackpkt, sock, addr)
            print("Server: Ack sent - %s", ack_to_send)


def main():
    """
    Main function to start the server.
    """
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = (HOST, port)
    sock.bind(server_address)
    
    # Choose protocol based on input
    if protocol == 0:
        snw_receiver(sock)
    elif protocol == 1:
        gbn_receiver(sock)

    
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
