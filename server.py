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
import udt, packet, timer


HOST = "127.0.0.1"
CACHE = "ServerCache/"
MSS = 1000


def create_checksum(i, data):
    '''
    Get sum of bits -> 1's Complement (Flip bits) = checksum
    '''
    # seq_bits = bin(i)[2:].zfill(4)  # test

    # data = seq_bits + data  # test

    dataSum = len(data)
    bitSum = bin(dataSum)[2:]

    # Pad to 10 bits
    while len(bitSum) < 10: # 10 before
        bitSum = '0' + bitSum

    checksum = ''
    for bit in bitSum:
        checksum += '1' if bit == '0' else '0'

    return checksum

# TODO: Add the seq to the checksum, that's what
def verify_checksum(i, checksum, data):
    print("server-verify-checksum: ", checksum)
    #print("checksum[:5]: ", checksum[:5])
    #print("checksum[-1]: ", int(checksum[5:]))
    # print("i: ", i)
    # if checksum[:5] == b'FIRST' and int(checksum[5:]) == i:
    #     return True
    # if checksum[:4] == b'DONE' and int(checksum[4:]) == i:
    #     return True
    
    # received_seq = int(checksum[:4], 2)
    # seq_bits = bin(i)[2:].zfill(4)  # test

    # seqSum = bin(received_seq + int(seq_bits, 2))
    # for bit in seqSum:
    #     if bit == '0':
    #         return False
    
    # logic to verify checksum
    # Add the sum and the checksum, if any 0 in found, corruption found
    if (checksum == b'DONE' or checksum == b'FIRST'): 
        print("Received done, time to finish")
        return True
    # if i + seq in checksum

    # received_seq = int(checksum[:4], 2)
    # if received_seq != i:
    #     return False
    
    dataSum = len(data)
    totalSum = dataSum + int(checksum, 2)
    totalSumBits = bin(totalSum)[2:]
    for bit in totalSumBits:
        if bit == '0':
            return False
    return True

def main():
    # Ask for a port number and the protocol to use
    if len(sys.argv) < 5:
        print('Usage : "python server.py -p port -r protocol (0 - SnW, 1 - GBN)"\n[port: port number that server will bind and listen on]\n[protocol: protocol the server will use (SnW or GBN)]')
        sys.exit(2)
    
    # Create dictionary with keys being the flags [-p, -r]
    args = {}
    for flag, value in zip(sys.argv[1::2], sys.argv[2::2]):
        args[flag] = value
    
    if '-p' not in args or '-r' not in args:
        print("Error: Missing required options.")
        sys.exit(2)
    
    # Variables we need
    port = int(args['-p'])
    protocol = int(args['-r'])

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = (HOST, port)
    sock.bind(server_address)
    seq = 0
    while True:
        pkt, addr = udt.recv(sock)
        print("server-pkt: ", pkt)
        print("server-addr: ", addr)
        seq, checksum, dataRcvd = packet.extract(pkt)
        print("server-seq rcvd: ", seq)
        print("server-checksum rcvd: ", checksum)
        print("Server: Pkt Received - ", dataRcvd)
        if verify_checksum(seq, checksum, dataRcvd):
            if checksum == b'DONE':
                print("in dataRcvd == DONE")
                sock.close()
                break
            if checksum == b'FIRST':
                extension = dataRcvd.decode("utf-8")
            if checksum != b"FIRST":
                # TODO: Save dataRcvd to servercache
                outputFile = f"{CACHE}{addr[0]}_{addr[1]}.{extension}"
                with open(outputFile, 'ab') as file:
                    file.write(dataRcvd)

            ackToSend = "ACK - " + str(seq % 2)
            print("acktosend: ", ackToSend)
            ackpkt = packet.make(seq % 2, create_checksum(seq % 2 , ackToSend).encode('utf-8'), bytes(ackToSend, 'utf-8'))   # TODO: all seq here, were originally i
            udt.send(ackpkt, sock, addr)
            print("Server: Ack sent - %s", ackToSend)
            

if __name__ == "__main__":
    main()