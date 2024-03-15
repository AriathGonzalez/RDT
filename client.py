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
import timer as t
import os


HOST = "127.0.0.1"
CACHE = "ClientCache/"
MSS = 1000


# TODO: What's the point of 'i' if you already add the seq # to the data before hand?
# Also, is it really this simple?
def create_checksum(i, data):
    '''
    Get sum of bits -> 1's Complement (Flip bits) = checksum
    '''
    # seq_bits = bin(i)[2:].zfill(4)  # test

    # data = seq_bits + data  # test

    dataSum = len(data)
    bitSum = bin(dataSum)[2:]
    print("client-bitSum: ", bitSum)
    # Pad to 10 bits
    while len(bitSum) < 10: # 10 before
        bitSum = '0' + bitSum

    checksum = ''
    for bit in bitSum:
        checksum += '1' if bit == '0' else '0'

    return checksum


def verify_checksum(i, checksum, data):
    # received_seq = int(checksum[:4], 2)
    # print("client-received-seq: ", received_seq)
    # seq_bits = bin(i)[2:].zfill(4)  # test
    # print("seq_bits: ", int(seq_bits, 2))

    # seqSum = bin(received_seq + int(seq_bits, 2))
    # for bit in seqSum:
    #     if bit == '0':
    #         return False
   

    print("client-checksum: ", checksum)
    print("client-data: ", data)
    # implement logic to verify checksum
    dataSum = len(data)
    totalSum = dataSum + int(checksum, 2)
    totalSumBits = bin(totalSum)[2:]
    for bit in totalSumBits:
        if bit == '0':
            return False
    return True


def main():
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
    filePath = CACHE + file

    if not os.path.exists(filePath):
        print("Error: File does not exist.")
        sys.exit(2)

    # Get chosen file from cache
    data = b''
    with open(filePath, 'rb') as file:
        data += file.read()

    # Separate data into packets of size 'MSS'
    # TODO: Ask if this is a good approach or what I should do instead.
    # Currently taking in all the data, and separating them into a list of strings, each string
    # being of size MSS or 1000
    dataPackets = [data[i:i + MSS] for i in range(0, len(data), MSS)]
    dataPackets.insert(0, extension)
    print("number of packets to send: ", len(dataPackets))
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)	 # making the socket non-blocking
    server_address = (HOST, port)

    mytimer = t.Timer(1)
    try:

        # Send data
        retransmissions = 0 # total transmissions
        actuallySent = 0

        while actuallySent < len(dataPackets):
            if actuallySent == 0:
                pkt = packet.make(actuallySent % 2, bytes("FIRST", "utf-8"), bytes(dataPackets[actuallySent], "utf-8"))
                udt.send(pkt, sock, server_address)
                print("Client: Initialization sent!")
            else:
                textToSend = dataPackets[actuallySent] # TODO: Should i keep this i to 0 or 1 for SnW; + str(actuallySent % 2)
                checksum = create_checksum(actuallySent % 2, textToSend).encode('utf-8')
                print("checksum now: ", checksum)
                pkt = packet.make(actuallySent % 2, checksum, textToSend)
                udt.send(pkt, sock, server_address)
                #textToSend = textToSend.decode("utf-8")
                #print("Client: Pkt sent - " + textToSend)

            # start timer
            mytimer.start()
            while mytimer.running() and not mytimer.timeout():
                # sock.settimeout(mytimer.time_left())

             
                rcvpkt, addr = udt.recv(sock)
                print("client-rcvpkt: ", rcvpkt)
                if rcvpkt:
                        seq, checksum, dataRcvd = packet.extract(rcvpkt)
                        if verify_checksum(seq, checksum, dataRcvd):
                            print("Client: Ack Received - %s", dataRcvd)
                            actuallySent += 1
                            mytimer.stop()
                print("continue?")
                continue
            mytimer.stop()
            print("i: ", retransmissions)
            print("actuallySent: ", actuallySent)
            print("len of packets: ", len(dataPackets))
            retransmissions += 1

    finally:
        textToSend = "DONE"
        pkt = packet.make(actuallySent % 2, bytes(textToSend, 'utf-8'))
        udt.send(pkt, sock, server_address)
        print("I am DONE sending")
        sock.close()


if __name__ == "__main__":
    main()