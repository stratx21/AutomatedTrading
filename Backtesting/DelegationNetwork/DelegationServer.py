import Backtesting.DelegationNetwork.server_config as server_config
import socket
import sys
import argparse
from _thread import start_new_thread

def clientConnectionThreadHandler(connection):
    connection.send(str.encode('Welcome to the Servern'))
    while 1:
        data = connection.recv(2048)
        reply = 'Server Says: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(reply))
    connection.close()

def runDelegationServer():
    serverSocket = socket.socket()
    host = server_config.host
    port = server_config.port
    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print("Error binding host and port:", str(e))
        return 

    threadCount = 0

    while 1:
        Client, address = serverSocket.accept()
        print("client at", address[0] + ":" + str(address[1]), "connected")
        start_new_thread(clientConnectionThreadHandler, (Client, ))
        threadCount += 1
        print("Clients connected:", str(threadCount))

    serverSocket.close()

