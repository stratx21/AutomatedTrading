from time import sleep
from Backtesting.DelegationNetwork.DelegationClient import runDelegationClient
from multiprocessing import Process
import sys 
import os
import CredentialsConfig.server_auth_config as server_auth_config

if __name__ == '__main__':
    try:
        processCount = int(sys.argv[1])

        if server_auth_config.tempStreamCopiesDirectory != None and not os.path.exists(server_auth_config.tempStreamCopiesDirectory):
            os.makedirs(server_auth_config.tempStreamCopiesDirectory)

        for i in range(processCount):
            print("starting process", str(i))
            Process(target = runDelegationClient, args=(str(i),)).start()
            sleep(1)

        print("all client drone processes started. ")
    except (ValueError, IndexError) as e:
        print("one argument of number of drone processes required.")