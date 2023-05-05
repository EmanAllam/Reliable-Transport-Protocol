from binascii import hexlify, unhexlify
import time
from Decapsulation import deSegment_ack, deSegment

#initializations
file_name = 'SmallFile.png'
Ip_address = ''
port_no = 5555
MSS = 1008 #maximum segment size
N = 5 #window size of Go-Back-N
time_out = 1 #time out value in seconds
ID_packet = 0
ID_file = 0
data_size = MSS - 8 #size of the payload in bytes
#byte ya3ny rkamen hexa
no_of_hexa = data_size * 2 #length of the payload in hexa
trailer = b'0' * 8


#reading the image in bytes and turning it into hexa digits
data = ''
raw_data = ''
with open(file=file_name, mode='rb') as image:
    raw_data = image.read()
    data = hexlify(raw_data)

print(f'data size: {len(data)}')
time.sleep(3)


#From here the server part
from socket import *

#socket initialization
data_skt = socket(AF_INET, SOCK_DGRAM)
ack_skt = socket(AF_INET, SOCK_DGRAM)

server_IP = 'localhost' #directly hyakhod IP al machine
port_no = 5555

data_skt.bind((server_IP, port_no)) #declare port ll server 3shan ba2y al clients tb3at 3aleh

N = N * no_of_hexa #window size in hexa

while(True):

    print('Here we go')
    message, sender_address = data_skt.recvfrom(4096) #unknown recv_socket (2ly hb3at 3aleh dataaa)

    confirmation = 'Here you go!'
    ack_skt.sendto(confirmation.encode(), sender_address)

    message = message.decode()

    base = 0 #base of the window
    thres = 0 #first unsent packet
    iterations = 0 #number of iterations (one iteration means finishing the packet ID space)
    last_ack = -1 #last acknowledged packet
    if message == 'small': #the small image
        j = 0
        while True:
            
            for j in range(thres, base + N, no_of_hexa): #sending the rest of the window
                if j + no_of_hexa >= len(data):
                    print('last')
                    trailer = b'f' * 8
                print(f'segment no. {ID_packet}')
                segment_data = data[j : j + no_of_hexa]
                segment = hexlify((ID_packet % 2**16).to_bytes(2)) + hexlify(ID_file.to_bytes(2)) + segment_data + trailer
                #time.sleep(0.0001)
                data_skt.sendto(segment, sender_address)

                ID_packet += int(len(segment_data) / 2)
                iterations = ID_packet // 2**16 #the iteration number of the last sent packet
            
            thres = base + N

            if trailer == b'f' * 8: #change thisss
                break
            
            ack = ack_skt.recv(4096) #receive acknowledgement

            ID_ack , _ID_file = deSegment_ack(ack) #decapsulation of the acknowledgment

            print(f'last ack {last_ack}, ack no. {ID_ack}')

            #update the base based on the acks, if base becomes outside the len(data) --> break as file is sent
            #two approaches: 1) 7awl ack id l equivalent byte address using no. of iterations 2)7awl base w base+N l equivalent ack id

            #trying second approach
            lower = (base // 2)  % 2**16 #lower base of the window
            upper = ((base + N) // 2) % 2**16 #upper base of the window

            #lw upper akbar mn lower fa enta tmam w lazem ack id mabenhom
            #lw lower akbar mn upper fa keda upper sabe2 b iteration w al ack id still akbar aw ad lower bs bardo akbar mn al upper

            #lw ack abl al window afkslha, lw ack ba3d al window afkslha
            #lw for packet alreaded acked then resend the window (2ly heya al packet 2ly ableya belzbt)
            #lw ack fel window, then update last acked, w update al base to last acked + 1
            
            print(f'lower is {lower}, upper is {upper}')
            if lower < upper:
                if ID_ack >= lower and ID_ack < upper: #keda al ack mazbota
                    last_ack = ID_ack
                    #update al base 3shan yb2a 2odam al last ack
                    diff = ID_ack - lower #difference ya3ny mabenhom kam byte
                    diff *= 2 #diff mabenhom kam hexa
                    base += diff * no_of_hexa
                    base += no_of_hexa
                elif ID_ack == last_ack:
                    thres = base #3shan ab3at akher window tani
                    ID_packet = ID_ack + int(len(segment_data) / 2) #synchronize the packet id m3 al window
                else:
                    pass #discard the ack lw heya akbar mn al window aw as8ar mnha except lw heya akher ack
            else:
                if ID_ack >= lower and ID_ack > upper or ID_ack < lower and ID_ack < upper: #lw al upper sabe2 al lower, ack gat 3and lower or gat 3and upper
                    last_ack = ID_ack
                    #update al base 3shan yb2a 2odam al last ack
                    if ID_ack < lower:
                        ID_ack += 2**16 #3shan akhleha fe mkanha akbar mnha 3shab a7seb al difference

                    diff = ID_ack - lower #difference ya3ny mabenhom kam byte
                    diff *= 2 #diff mabenhom kam hexa
                    base += diff * no_of_hexa
                    base += no_of_hexa
                elif ID_ack == last_ack:
                    thres = base #3shan ab3at akher window tani
                    ID_packet = ID_ack + int(len(segment_data) / 2) #synchronize the packet id m3 al window
                else:
                    pass #discard the ack lw heya akbar mn al window aw as8ar mnha except lw heya akher ack

    ID_file += 1