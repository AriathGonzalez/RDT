# packet.py - Packet-related functions

# Creates a packet from a sequence number and byte data
def make(seq_num, checksum, data = b''):
    print("in make: ", seq_num)
    print("in checksum: ", checksum)
    print("in make: data: ", data)
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    print("seq_bytes-type: ", type(seq_bytes))
    print("checksum-type: ", type(checksum))
    print("data-type: ", type(data))
    return seq_bytes + checksum + data

# Creates an empty packet
def make_empty():
    return b''

# Extracts sequence number and data from a non-empty packet
def extract(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    # First
    print("packet-first? ", packet[4:9])
    if packet[4:9] == b'FIRST':
        checksum = packet[4:9]
        return seq_num, checksum, packet[9:]
    
    checksum = packet[4:14] # TODO: Originally 4:12, changed it to 4:14 since 1000 is max 10 bits in binary
    print("in extract, checksum: ", checksum)
    return seq_num, checksum, packet[14:]