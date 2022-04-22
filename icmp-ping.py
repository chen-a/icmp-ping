import socket
import time
import select
import struct

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

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
    #Pyload includes a timestamp
    checkSumPacket = struct.pack("!BBHHHd", 8, 0, 0, 1000, sequence, time.time())
    checksumValue = checksum(checkSumPacket)
    realPacket = struct.pack("!BBHHHd", 8, 0, checksumValue, 1000, sequence, time.time())

    #sendto(bytes, address) since socket is not connected
    clientSocket.sendto(realPacket, (destinationAddress, 2424))
    print("packet sent")

def getEchoResponse(destinationAddress, sequence):
    sendEchoRequest(destinationAddress, sequence)
        #clientSocket.setblocking(0)
        #readyObject = select.select([clientSocket], [], [], 1)
        #if readyObject[0]:
         #   response = clientSocket.recv(1508)
    timeout = time.time() + 1
    while True:
        response = clientSocket.recv(1024)
        timeReceived = time.time()
        if response is not None:
            if time.time() >= timeout:
                return None
            else:
                print("packet received")
                #B size = 1 byte = 8 bit
                #H size = 2 bytes= 16 bit
                #d size = 8 bytes = 64 bit
                #BBHHHd size = 16 bytes
                #ICMP header starts at 160 bits = 20 bytes
                start = 20
                end = 20 + (struct.calcsize("!B") * 2) + (struct.calcsize("H") * 3) + struct.calcsize("!d")
                header = response[start:end]
                type, code, checkSum, ID, rSequence, timeSent = struct.unpack("!BBHHHd", header)
                print("type = " + str(type) + " checkSum = " + str(checkSum) + " ID + " + str(ID) + " sequence = " + str(rSequence) + " pay = " + str(timeSent))
                return timeReceived - timeSent
    
i = 0
while True:
    message = input()
    command = message.split()[0]
    if command == 'ping':
        destination = message.split()[1]
        destinationAddress = socket.gethostbyname(destination)
        while True:
            var = getEchoResponse(destinationAddress, i)
            if var is None:
                print("var is none")
            else:
                print("var = " + str(var))
            i += 1
            time.sleep(1)



    else:
        print("Error: Invalid Command. Please try again")

clientSocket.close()

'''
while True:
    message = input()
    command = message.split()[0]
    if command == 'ping':
        #try:
            destination = message.split()[1]
            destinationAddress = socket.gethostbyname(destination)
            while True:
                print("here1")
                var = getEchoResponse(destinationAddress)
                print("here2")
                if var is None:
                    print("var is none")
                else:
                    print("var = " + var)
                time.sleep(1)
            
    
        #except:
         #   print ("Error: Destination Invalid. Please try again")

    else:
        print("Error: Invalid Command. Please try again")
'''
    