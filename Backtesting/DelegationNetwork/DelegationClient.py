import CredentialsConfig.server_auth_config as server_auth_config
import Backtesting.DelegationNetwork.server_config as delegation_server_config
import socket 

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
    
    response = clientSocket.recv(1024)
    while 1:
        inputstr = input("entry: ")
        clientSocket.send(str.encode(inputstr))
        response = clientSocket.recv(1024)
        print(response.decode('utf-8'))





