import socket
import time
import struct

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
#allows socket.recv to continue if nothing is there
clientSocket.setblocking(0)
def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer 

def sendEchoRequest(destinationAddress, sequence):
    #Message type 8 and code 0 is an echo request
    #Initial Checksum value is 0
    #8 bit int is B
    #16 bit int is H 
    #64 bit double is d
    #! indicates network byte order
    #Pyload includes a timestamp
    checkSumPacket = struct.pack("!BBHHHd", 8, 0, 0, 1001, sequence, time.time())
    checksumValue = checksum(checkSumPacket)
    realPacket = struct.pack("!BBHHHd", 8, 0, checksumValue, 1001, sequence, time.time())

    #sendto(bytes, address) since socket is not connected
    clientSocket.sendto(realPacket, (destinationAddress, 2424))

def getEchoResponse(destinationAddress, sequence):
    sendEchoRequest(destinationAddress, sequence)
    timeout = time.time() + 1
    while True:
        if time.time() > timeout:
            return None
        try:
            response = clientSocket.recv(1024)
            timeReceived = time.time()
            if response is not None:
                #B size = 1 byte = 8 bit
                #H size = 2 bytes= 16 bit
                #d size = 8 bytes = 64 bit
                #BBHHHd size = 16 bytes
                #ICMP header starts at 160 bits = 20 bytes
                start = 20
                end = 20 + (struct.calcsize("!B") * 2) + (struct.calcsize("H") * 3) + struct.calcsize("!d")
                header = response[start:end]
                type, code, checkSum, ID, rSequence, timeSent = struct.unpack("!BBHHHd", header)
                if ((type == 0) and (code == 0) and (ID == 1001) and (rSequence == sequence)):
                    return timeReceived - timeSent
                else:
                    return None
        except:
            pass
            
    
i = 0
print("Please enter 'ping' followed by an address. Example: ping www.google.com")
while True:
    message = input()
    command = message.split()[0]
    if command == 'ping':
        try:
            destination = message.split()[1]
            destinationAddress = socket.gethostbyname(destination)
            print("\nPinging " + destination + " (" + str(destinationAddress) + "):")
            while True:
                delay = getEchoResponse(destinationAddress, i)
                if delay is None:
                    print("Packet timed out: Sequence = " + str(i))
                else:
                    #convert seconds to ms
                    delay *= 1000
                    print("Reply from " + str(destinationAddress) + ": Sequence = " + str(i) + " Delay = " + ("%.0f" % delay) + "ms")
                i += 1
                time.sleep(1)
        except:
            print ("Error: Destination Invalid. Please try again!")
    else:
        print("Error: Invalid Command. Please try again!")

clientSocket.close()
