from Backtesting.DelegationNetwork.DelegationClient import runDelegationClient
from multiprocessing import Process
import sys 

if __name__ == '__main__':
    try:
        processCount = int(sys.argv[1])

        for i in range(processCount):
            print("starting process", str(i))
            Process(target = runDelegationClient, args=(str(i),)).start()

        print("all client drone processes started. ")
    except (ValueError, IndexError) as e:
        print("one argument of number of drone processes required.")