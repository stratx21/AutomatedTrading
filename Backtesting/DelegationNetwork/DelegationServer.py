from DataManagement.Database.HoldProfitTable import updateHoldProfitTable
from Backtesting.DelegationNetwork.WorkManager import WorkManager
import Backtesting.DelegationNetwork.server_config as server_config
import socket
from _thread import start_new_thread
import threading
import Backtesting.DelegationNetwork.DelegationTransferStrings as DTS
import struct

threadLock = threading.Lock() 
workManager = WorkManager()

def clientConnectionThreadHandler(connection, dbCursor):
    connection.send(str.encode('Connection with server initialized'))
    outOfWork = False 
    while not outOfWork:
        data = connection.recv(2048)
        if not data:
            print("data was None!")
            break
        dataStr = data.decode('utf-8')
        # print("data from client:", dataStr)

        reply = DTS.INVALID
        if dataStr == DTS.WORK_REQUEST:
            threadLock.acquire()
            reply = workManager.getWorkJson(dbCursor)
            threadLock.release()

        if reply == None:
            print("out of work to delegate, closing connection")
            outOfWork = True
            reply = DTS.OUT_OF_WORK

        reply = struct.pack('>I', len(reply)) + str.encode(reply) 
        connection.sendall(reply)
    connection.close()
    print("connection closed")

    if outOfWork:
        exit()

def runInitHoldProfitTableUpdate(connection, dbCursor):
    updateHoldProfitTable(workManager.getAllFilenames(), dbCursor)

def runInitWorkUpdate(connection, dbCursor):
    threadLock.acquire()
    workManager.updateWorkQueue(dbCursor)
    threadLock.release()
    runInitHoldProfitTableUpdate(connection, dbCursor)

def runDelegationServer(dbConnection, dbCursor):
    serverSocket = socket.socket()
    host = server_config.host
    port = server_config.port
    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print("Error binding host and port:", str(e))
        return 

    threading.Thread(target = runInitWorkUpdate, args = (dbConnection, dbCursor)).start()

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

