import CredentialsConfig.server_auth_config as server_auth_config
import Backtesting.DelegationNetwork.server_config as delegation_server_config
import socket 
import time 
import datetime
from Tools.StringTools import secondsToTimeDescription

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
        response = clientSocket.recv(1024)
        print(response.decode('utf-8'))


    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("Client finished!", 
        "End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        secondsToTimeDescription(elapsedSeconds))


