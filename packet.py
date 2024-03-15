# packet.py - Packet-related functions

# Creates a packet from a sequence number and byte data
def make(seq_num, checksum, data = b''):
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    return seq_bytes + checksum + data

# Creates an empty packet
def make_empty():
    return b''

# Extracts sequence number and data from a non-empty packet
def extract(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    if packet[4:9] == b'FIRST':
        checksum = packet[4:9]
        return seq_num, checksum, packet[9:]
    
    checksum = packet[4:14] # TODO: Originally 4:12, changed it to 4:14 since 1000 is max 10 bits in binary
    return seq_num, checksum, packet[14:]
