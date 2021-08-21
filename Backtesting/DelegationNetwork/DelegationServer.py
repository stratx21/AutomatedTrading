from Backtesting.DelegationNetwork.WorkManager import WorkManager
import Backtesting.DelegationNetwork.server_config as server_config
import socket
from _thread import start_new_thread
import threading
import Backtesting.DelegationNetwork.DelegationTransferStrings as DTS

threadLock = threading.Lock() 
workManager = WorkManager()

def clientConnectionThreadHandler(connection, dbCursor):
    connection.send(str.encode('Welcome to the Server'))
    while 1:
        data = connection.recv(2048)
        print("data from client:", str(data))
        if not data:
            print("data was None!")
            break
        reply = DTS.INVALID
        if data == DTS.WORK_REQUEST:
            threadLock.acquire()
            reply = workManager.getWorkJson(dbCursor)
            threadLock.release()
        connection.sendall(str.encode(reply))
    connection.close()
    print("connection closed", str(connection))

def runDelegationServer(dbCursor):
    serverSocket = socket.socket()
    host = server_config.host
    port = server_config.port
    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print("Error binding host and port:", str(e))
        return 

    print("Running server at " + host + ":" + str(port))
    print(" Waiting for connections...")
    threads = []
    threadCount = 0
    while 1:
        serverSocket.listen(20)
        Client, address = serverSocket.accept()
        print("client at", address[0] + ":" + str(address[1]), "connected")
        # start_new_thread(clientConnectionThreadHandler, (Client, ))
        thread = threading.Thread(target = clientConnectionThreadHandler, args = (Client, dbCursor))
        thread.start()
        threads.append(thread)
        threadCount += 1
        print("total connections initiated:", str(threadCount))

    serverSocket.close()

