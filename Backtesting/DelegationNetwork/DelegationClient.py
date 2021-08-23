import json
import sys
import os
import CredentialsConfig.server_auth_config as server_auth_config
import Backtesting.DelegationNetwork.server_config as delegation_server_config
import Backtesting.DelegationNetwork.DelegationTransferStrings as DTS
from Backtesting.DelegationNetwork.DelegationDrone import runDrone
from mysql.connector import connect, Error 
import socket 
import time 
import datetime
import struct
import shutil
from Tools.StringTools import getTickerFromFilename, secondsToTimeDescription

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






def runDelegationClient(id):
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

    try:
        with connect(
            host=server_auth_config.host,
            user=server_auth_config.userDB,
            password=server_auth_config.passwordDB,
            database=server_auth_config.database
        ) as connection, connection.cursor() as cursor:

            response = clientSocket.recv(1024)
            while 1:
                inputstr = DTS.WORK_REQUEST
                clientSocket.send(str.encode(inputstr))
                response = recv_msg(clientSocket).decode('utf-8')

                if response == DTS.OUT_OF_WORK:
                    print("Drone", id, "finished, no more work.")
                    break

                responseDict = json.loads(response)
                strats = responseDict[DTS.STRATEGIES_KEY]
                filename = responseDict[DTS.FILENAME_KEY]
                ticker = getTickerFromFilename(filename)

                # copy over file if it isn't there already 
                if server_auth_config.tempStreamCopiesDirectory != None and not os.path.isfile(server_auth_config.tempStreamCopiesDirectory + filename):
                    print("copying " + server_auth_config.streamRecordsDirectory + filename + " to " + server_auth_config.tempStreamCopiesDirectory)
                    shutil.copy(server_auth_config.streamRecordsDirectory + filename, server_auth_config.tempStreamCopiesDirectory)

                print("Drone", id, "starting new work on", str(len(strats)), "strategies for", ticker)
                runDrone(
                    strats,
                    filename,
                    ticker,
                    cursor,
                    connection)

    except Error as e:
        print("error with db: ", e)
    except: 
        print("ERROR: delegation client non-db error:", sys.exc_info()[0])

    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("Drone", id, "finished!", 
        "elapsed time:", 
        secondsToTimeDescription(elapsedSeconds))


