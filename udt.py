# udt.py - Unreliable data transfer using UDP
import random
import socket


DROP_PROB = .5
CORR_PROB = .5

# Send a packet across the unreliable channel
# Packet may be lost or corrupted
def send(packet, sock, addr):
    if random.randint(0, 10) > DROP_PROB:
        sock.sendto(packet, addr)

# Receive a packet from the unreliable channel
def recv(sock):
    try:
        packet, addr = sock.recvfrom(1024)
        return packet, addr
    except socket.error:
        return None, None
