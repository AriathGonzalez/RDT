# udt.py - Unreliable data transfer using UDP
import random
import socket


DROP_PROB = .5
CORR_PROB = .5

# Send a packet across the unreliable channel
# Packet may be lost or corrupted
def send(packet, sock, addr):
    if random.randint(0, 10) > DROP_PROB:
        print("UDT: sending pkt: ", packet)
        sock.sendto(packet, addr)
    return

# Receive a packet from the unreliable channel
def recv(sock):
    try:
        packet, addr = sock.recvfrom(1024)
        print("UDT-pkt: ", packet)
        print("UDT-addr: ", addr)
        return packet, addr
    except socket.error:
        return None, None

