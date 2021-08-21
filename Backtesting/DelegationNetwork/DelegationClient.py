import CredentialsConfig.server_auth_config as server_auth_config
import Backtesting.DelegationNetwork.server_config as delegation_server_config
import socket 
import time 
import datetime
import struct
from Tools.StringTools import secondsToTimeDescription

BUFFER_SIZE = 4096

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, length):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def runDelegationClient():
    clientSocket = socket.socket()
    host = server_auth_config.host 
    port = delegation_server_config.port 

    print("connecting to " + host + ":" + str(port) + " ...")
    try:
        clientSocket.connect((host, port))
    except socket.error as e:
        print("Error connecting to server:", str(e))
        return 
    
    start_timer = time.time()

    response = clientSocket.recv(1024)
    while 1:
        inputstr = input("entry: ")
        clientSocket.send(str.encode(inputstr))
        response = recv_msg(clientSocket)
        print(response.decode('utf-8'))


    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("Client finished!", 
        "End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        secondsToTimeDescription(elapsedSeconds))


