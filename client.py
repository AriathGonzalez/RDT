'''
This is the sender program, this will be started second.

Send data along w/ sequence # (0, 1); Start Timer()
- Wait for ACK (in time)
    - checksum() correct data and sequence # (0, 1)
        - stopTimer()
    - Retransmit data w/ sequence # (0, 1)
- else: timeout() -> Retransmit data w/ sequence # (0, 1)
Note: We will keep doing this until file fully sends as MSS is 1000 bytes.
'''
import socket
import sys
import udt, packet
import timer as t, time
import os


# Constants
HOST = "127.0.0.1"
CACHE = "ClientCache/"
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
    received_checksum = create_checksum(i, data).encode("utf-8")

    return checksum == received_checksum


def print_summary(total_transmitted_packets, retransmissions, transmission_time):
    # i. Total number of transmitted packets.
    print("Total number of transmitted packets: ", total_transmitted_packets)
    # ii. Number of retransmitted packets:
    print("Number of retransmitted packets: ", retransmissions)
    # iii. Time taken to complete file transfer.
    print("Time taken to complete file transfer: ", transmission_time)


def snw_sender(sock, server_address, data_packets):
    """
    Sends packets using Stop-and-Wait protocol.

    Parameters:
    - sock (socket.socket): The UDP socket to send packets on.
    - server_address (tuple): The server's (host, port) tuple.
    - data_packets (list): List of data packets to send.
    """
    start_time = time.time()
    mytimer = t.Timer(1)
    try:
        total_transmitted_packets = 0 # Total transmissions
        transmitted_packets = 0 # Packets actually sent

        # Attempt to send packets
        while transmitted_packets < len(data_packets):
            if transmitted_packets == 0:
                pkt = packet.make(transmitted_packets % 2, bytes("FIRST", "utf-8"), bytes(data_packets[transmitted_packets], "utf-8"))
                udt.send(pkt, sock, server_address)
                print("Client: initialization sent!")
            else:
                text_to_send = data_packets[transmitted_packets] 
                checksum = create_checksum(transmitted_packets % 2, text_to_send).encode("utf-8")
                pkt = packet.make(transmitted_packets % 2, checksum, text_to_send)
                udt.send(pkt, sock, server_address)
                print("Client: Pkt sent - ", text_to_send)

            # Start timer, wait for acknowledgment of packets previously sent
            mytimer.start()
            while mytimer.running() and not mytimer.timeout():
                rcvpkt, _ = udt.recv(sock)
                if rcvpkt:
                        seq, checksum, data_rcvd = packet.extract(rcvpkt)
                        # Acknowledgement received, go to next packet
                        if verify_checksum(seq, checksum, data_rcvd):
                            print("Client: Ack Received - %s", data_rcvd)
                            transmitted_packets += 1
                            total_transmitted_packets += 1
                            mytimer.stop()
                continue
            # Timeout, resend packet
            mytimer.stop()
            total_transmitted_packets += 1

    # Finished sending all packets, send "DONE" signal
    finally:
        text_to_send = "DONE"
        pkt = packet.make(transmitted_packets % 2, bytes(text_to_send, 'utf-8'))
        udt.send(pkt, sock, server_address)
        print("I am DONE sending")

        end_time = time.time()
        transmission_time = end_time - start_time
        retransmissions = total_transmitted_packets - transmitted_packets

        # Summary
        print_summary(total_transmitted_packets, retransmissions, transmission_time)
        sock.close()


def gbn_sender(sock, server_address, data_packets):
    """
    Sends packets using Go-Back-N protocol.

    Parameters:
    - sock (socket.socket): The UDP socket to send packets on.
    - server_address (tuple): The server's (host, port) tuple.
    - data_packets (list): List of data packets to send.
    """
    send_base = 0       # The start of sent, not yet ack'ed (Yellow) packets
    next_seq_num = 0    # The first usable, not yet sent (Blue) packet
    send_window = []    # The current window

    start_time = time.time()
    mytimer = t.Timer(1)
    try:
        total_transmitted_packets = 0
        number_of_timeouts = 0
        # send_base: Number of already ack'ed packets + 1 or (# Green + 1)
        while send_base < len(data_packets):
            # Attempt to send window_size packets at a time
            while next_seq_num < min(send_base + window_size, len(data_packets)):
                # Construct and send packet
                if next_seq_num == 0:
                    pkt = packet.make(0, bytes("FIRST", "utf-8"), bytes(data_packets[next_seq_num], "utf-8"))
                    udt.send(pkt, sock, server_address)
                    print("Client: initialization sent!")
                else:
                    text_to_send = data_packets[next_seq_num]
                    checksum = create_checksum(next_seq_num, text_to_send).encode("utf-8")
                    pkt = packet.make(next_seq_num, checksum, text_to_send)
                    udt.send(pkt, sock, server_address)
                    print("Client: Pkt sent - ", text_to_send)
                
                # Store packet in the send window
                # These will be the sent, not yet ack'ed (Yellow) packets
                send_window.append(next_seq_num)
                next_seq_num += 1

            # Start timer, and wait for acknowledgement for the previously sent packets
            mytimer.start()    
            while mytimer.running() and not mytimer.timeout():
                rcvpkt, _ = udt.recv(sock)
                if rcvpkt:
                    seq, checksum, data_rcvd = packet.extract(rcvpkt)
                    if verify_checksum(seq, checksum, data_rcvd):
                        print("Client: Ack Received - %s", data_rcvd)
                        seq = int(data_rcvd.decode("utf-8").split('-')[-1])     # Get ACK # in data
                        # Slide the window forward
                        if send_window and send_window[0] == seq:
                            '''
                            Timer has not timed out!
                            Therefore, the next_seq_num will be incremented
                            The first packet in the send_window has gotten the ACK (Green), so pop it
                            Meaning, the send_base shall also increment
                            Finally, exit the inner loop and go back to the outer loop IMMEDIATELY
                            '''
                            mytimer.stop()
                            next_seq_num = send_window[-1] + 1    
                            send_window.pop(0)
                            total_transmitted_packets += 1
                            send_base = seq + 1
                            break
                continue
            if not mytimer.timeout(): continue  # To go back to outer loop

            # Handle timeout for unacknowledged packets
            mytimer.stop()
            total_transmitted_packets += len(send_window)   # Retransmit all packets in the current window
            next_seq_num = send_base    # next_seq_num will start from the beginning
            send_window = []    # Will resend all packets, so current window must reset
            number_of_timeouts += 1

    # Finished sending all the packets, send "DONE" signal
    finally:
        text_to_send = "DONE"
        pkt = packet.make(next_seq_num, bytes(text_to_send, 'utf-8'))
        udt.send(pkt, sock, server_address)
        print("I am DONE sending")

        end_time = time.time()
        transmission_time = end_time - start_time
        retransmissions = total_transmitted_packets - len(data_packets)

        # Summary
        print_summary(total_transmitted_packets, retransmissions, transmission_time)
        print("Number of timeouts: ", number_of_timeouts)
        sock.close()


def main():
    """
    Main function to start the client.
    """
    # Get chosen file from cache
    data = b''
    with open(file_path, "rb") as file:
        data += file.read()
        
    # Separate data into packets of size 'MSS'
    data_packets = [data[i:i + MSS] for i in range(0, len(data), MSS)]
    # Calculate number needed to determine the number of packets transmitted for the server side
    max_packets_transmitted = 2 if protocol == 0 else len(data_packets) + 1
    data_packets.insert(0, extension + f":{max_packets_transmitted}")
    print("num of packets: ", len(data_packets) + 2)
    print("last packet: " ,data_packets[0])

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)	 # making the socket non-blocking
    server_address = (HOST, port)

    if protocol == 0:
        snw_sender(sock, server_address, data_packets)
    elif protocol == 1:
        gbn_sender(sock, server_address, data_packets)


if __name__ == "__main__":
    # Ask for a port number and the protocol to use
    if len(sys.argv) < 9:
        print('Usage : "python client.py -p port -r protocol -f file -n window_size (0 - SnW, 1 - GBN)"\n[port: port number of the server to connect]\n[protocol: protocol the server will use (SnW or GBN)]\n[file: file that will be sent to server]\n[window_size: window size used by the sender/receiver in GBN]')
        sys.exit(2)
    
    # Parse command-line arguments
    args = {}
    for flag, value in zip(sys.argv[1::2], sys.argv[2::2]):
        args[flag] = value
    
    if '-p' not in args or '-r' not in args or '-f' not in args or '-n' not in args:
        print("Error: Missing required options.")
        sys.exit(2)
    
    # Variables we need
    port = int(args['-p'])
    protocol = int(args['-r'])
    file = args['-f']
    window_size = int(args['-n'])

    extension = file.split('.')[-1].lower()
    file_path = CACHE + file

    # Ensure file exists
    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        sys.exit(2)

    main()
