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


HOST = "127.0.0.1"
CACHE = "ClientCache/"
MSS = 1000


# TODO: What's the point of 'i' if you already add the seq # to the data before hand?
# Also, is it really this simple?
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

# TODO: do i need to do the htons and ntohns stuff or nah?
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
    data_sum = len(data)
    total_sum = data_sum + int(checksum, 2)
    total_sum_bits = bin(total_sum)[2:]
    
    for bit in total_sum_bits:
        if bit == '0':
            return False
    return True


def main():
    # Get chosen file from cache
    data = b''
    with open(file_path, 'rb') as file:
        data += file.read()

    # Separate data into packets of size 'MSS'
    # TODO: Ask if this is a good approach or what I should do instead.
    # Currently taking in all the data, and separating them into a list of strings, each string
    # being of size MSS or 1000
    data_packets = [data[i:i + MSS] for i in range(0, len(data), MSS)]
    data_packets.insert(0, extension)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)	 # making the socket non-blocking
    server_address = (HOST, port)

    start_time = time.time()
    mytimer = t.Timer(1)
    try:
        # Send data
        total_transmitted_packets = 0 # Total transmissions
        transmitted_packets = 0 # Actually sent

        while transmitted_packets < len(data_packets):
            if transmitted_packets == 0:
                pkt = packet.make(transmitted_packets % 2, bytes("FIRST", "utf-8"), bytes(data_packets[transmitted_packets], "utf-8"))
                udt.send(pkt, sock, server_address)
                print("Client: initialization sent!")
            else:
                text_to_send = data_packets[transmitted_packets]# TODO: Should i keep this i to 0 or 1 for SnW; + str(actuallySent % 2)
                checksum = create_checksum(transmitted_packets % 2, text_to_send).encode('utf-8')
                pkt = packet.make(transmitted_packets % 2, checksum, text_to_send)
                udt.send(pkt, sock, server_address)
                print("Client: Pkt sent - ", text_to_send)

            # Start timer
            mytimer.start()
            while mytimer.running() and not mytimer.timeout():
                rcvpkt, _ = udt.recv(sock)
                if rcvpkt:
                        seq, checksum, data_rcvd = packet.extract(rcvpkt)
                        if verify_checksum(seq, checksum, data_rcvd):
                            print("Client: Ack Received - %s", data_rcvd)
                            transmitted_packets += 1
                            total_transmitted_packets += 1
                            mytimer.stop()
                continue
            mytimer.stop()
            total_transmitted_packets += 1

    finally:
        text_to_send = "DONE"
        pkt = packet.make(transmitted_packets % 2, bytes(text_to_send, 'utf-8'))
        udt.send(pkt, sock, server_address)
        print("I am DONE sending")

        end_time = time.time()
        transmission_time = end_time - start_time
        retransmissions = total_transmitted_packets - transmitted_packets

        # Summary
        # i. Total number of transmitted packets.
        print("Total number of transmitted packets: ", total_transmitted_packets)
        # ii. Number of retransmitted packets:
        print("Number of retransmitted packets: ", retransmissions)
        # iii. Time taken to complete file transfer.
        print("Time taken to complete file transfer: ", transmission_time)
        sock.close()


if __name__ == "__main__":
    # Ask for a port number and the protocol to use
    if len(sys.argv) < 7:
        print('Usage : "python client.py -p port -r protocol -f file (0 - SnW, 1 - GBN)"\n[port: port number of the server to connect]\n[protocol: protocol the server will use (SnW or GBN)]\n[file: file that will be sent to server]')
        sys.exit(2)
    
    # Create dictionary with keys being the flags [-p, -r]
    args = {}
    for flag, value in zip(sys.argv[1::2], sys.argv[2::2]):
        args[flag] = value
    
    if '-p' not in args or '-r' not in args or '-f' not in args:
        print("Error: Missing required options.")
        sys.exit(2)
    
    # Variables we need
    port = int(args['-p'])
    protocol = int(args['-r'])
    file = args["-f"]

    extension = file.split('.')[-1].lower()
    file_path = CACHE + file

    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        sys.exit(2)

    main()
