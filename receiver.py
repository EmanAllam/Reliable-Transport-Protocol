from socket import *
from binascii import hexlify, unhexlify
from Decapsulation import deSegment
import random
import time

raw_data = b''
with open(file='SmallFile.png', mode='rb') as image:
    raw_data = image.read()

data_skt = socket(AF_INET, SOCK_DGRAM)
ack_skt = socket(AF_INET, SOCK_DGRAM)

#for sending
server_IP = 'localhost'
port_no = 1234 #choose from registered ports (1024, 49___)

ack_skt.bind((server_IP, port_no))

while True:
    data = bytes()
    message = input('input message: ')

    data_skt.sendto(message.encode(), (server_IP, 5555))

    confirmation, sender_address = data_skt.recvfrom(4096) #sender address da hb3at 3aleh acksss

    print(confirmation.decode())

    expected = 0
    last_correct = 0
    while True:
        #time.sleep(0.0001)
        segment = data_skt.recv(4096) #input buffer size (powers of 2)

        ID_packet, ID_file, datum, trailer, length = deSegment(segment) #check trailer thing

        if ID_packet < expected: #lw ack l haga adema afkslha
            continue

        #some randomness to check out of order packets
        rand = random.randint(0, 100)
        if rand <= 20 and ID_packet != 0:
            print(f'error at: {ID_packet}')
            ID_packet += 100


        if ID_packet != expected: #lw msh al expected ab3at al last correct ack
            ack = hexlify(last_correct.to_bytes(2)) + hexlify(ID_file.to_bytes(2))
            print(f'recieved {ID_packet}, but not as expected {expected}')
            ack_skt.sendto(ack, sender_address)
            continue

        #lw expected
        print(f'received ID: {ID_packet}')
        last_correct = ID_packet
        expected += int(length / 2)
        expected %= 2**16
        
        data += datum

        #send ack
        ack = hexlify(ID_packet.to_bytes(2)) + hexlify(ID_file.to_bytes(2))
        ack_skt.sendto(ack, sender_address)

        if trailer == b'f' * 8:
            break
    
    with open('receiver3.png', 'wb') as f:
        f.write(data)

    print(raw_data == data)


#recv_skt.close()