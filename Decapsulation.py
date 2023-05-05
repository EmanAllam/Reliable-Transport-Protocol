from binascii import hexlify, unhexlify

def deSegment(segment):
    length = len(segment[8 : len(segment) - 8])
    ID_packet = unhexlify(segment[0 : 4])
    ID_file = unhexlify(segment[4 : 8])
    data = unhexlify(segment[8 : len(segment) - 8])
    trailer = segment[-8:]

    return (int.from_bytes(ID_packet), int.from_bytes(ID_file), data, trailer, length)

def deSegment_ack(ack):
    ID_packet = unhexlify(ack[0 : 4])
    ID_file = unhexlify(ack[4 : 8])

    return (int.from_bytes(ID_packet), int.from_bytes(ID_file))

