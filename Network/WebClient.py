from websockets import client, exceptions
import Terminal.TerminalStrings as TerminalStrings
import asyncio
import json
import sys 

class WebClient():
    sendDataPipe = None 
    uri = None 

    def __init__(self, sendDataPipe):
        self.data_holder = []
        self.cnxn = None
        self.crsr = None
        self.sendDataPipe = sendDataPipe

    def __exit__(self, exc_type, exc_value, traceback):
        print("entered web client EXIT...")
        self.disconnect()

    def __del__(self):
        print("entered web client DELETE...")
        self.disconnect()
        

    async def connect(self, uri):
        '''
            Connecting to webSocket server
            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''

        self.connection = await client.connect(uri)
        self.uri = uri 
        # let the user know it connecte
        if self.connection.open:
            print(TerminalStrings.SYS_MESSAGE + " Connection established. Client correctly connected")
            return self.connection

        print("Connection failed to open. Connection: ", self.connection)


    async def sendMessage(self, message):
        '''
            Sending message to webSocket server
        '''
        await self.connection.send(message)
        

    async def receiveMessage(self, connection):
        '''
            Receiving all server messages and handle them
        '''
        while True:
            try:
                # grab and decode the message
                message = await connection.recv() 
                message_decoded = json.loads(message)
                
                # check if the response contains a key called data if so then it contains the info we want to insert.
                if 'data' in message_decoded.keys():
                    
                    # grab the data
                    data = message_decoded['data'][0]
                    
                    # print('-'*20)
                    # print('Received message from server: ' + str(message))

                    self.sendDataPipe.send(json.dumps(data))
                    # print("Data retrieved from server: ", data)
                    
                # print('-'*20)
                # print('Received message from server: ' + str(message))
                
            except exceptions.ConnectionClosed:            
                print('Connection with server closed')
                break
            except:
                print("error in receive message: ", sys.exc_info()[0])

                
    async def heartbeat(self, connection):
        '''
            Sending heartbeat to server every 5 seconds
            Ping - pong messages to verify connection is alive
        '''
        while True:
            try:
                await connection.send('ping')
                await asyncio.sleep(5)
            except exceptions.ConnectionClosed:
                print('Connection with server closed')
                break




    def disconnect(self):
        if self.connection.open:
            print("closing connection to TDA...")
            self.connection.close()
            print("closed connection to TDA")