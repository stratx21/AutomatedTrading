from Network.WebClient import WebClient
import asyncio
import json
import urllib
import DataManagement.Auth.auth as auth
import  config 
from dateutil.parser import parse
import requests, datetime
import time 
from math import ceil 
import nest_asyncio
import Terminal.TerminalStrings as TerminalStrings
import DataManagement.DataTransferStrings as DataTransferStrings
import CredentialsConfig.TDA_auth_config as TDA_auth_config

nest_asyncio.apply()


def unix_time_millis(dt):
    # grab the starting point, so time '0'
    epoch = datetime.datetime.utcfromtimestamp(0)
    
    return (dt - epoch).total_seconds() * 1000.0
    

class TDAMeritrade: 
    sendDataPipe = None 
    userPrincipalsResponse = None 

    def __init__(self, sendDataPipe):
        self.sendDataPipe = sendDataPipe


    # start streaming - process run to stay in this function, and
    # retrieve data for the provided tickers until the process is
    # terminated. 
    async def startStreaming(self, tickersString, isJH2 = False, getOnlyLastPrice = False):
        #start streaming connection: 
        streamingEndpoint = "https://api.tdameritrade.com/v1/userprincipals"
        params = {'fields':'streamerSubscriptionKeys,streamerConnectionInfo'}
        headers = {'Authorization': auth.getAuthString(isJH2)}
        content = requests.get(url = streamingEndpoint, params = params, headers = headers)
        userPrincipalsResponse = content.json()
        self.userPrincipalsResponse = userPrincipalsResponse

        tokenTimeStamp = userPrincipalsResponse['streamerInfo']['tokenTimestamp']
        date = parse(tokenTimeStamp, ignoretz = True)
        tokenTimeStampAsMs = unix_time_millis(date)

        credentials = {"userid": userPrincipalsResponse['accounts'][0]['accountId'],
               "token": userPrincipalsResponse['streamerInfo']['token'],
               "company": userPrincipalsResponse['accounts'][0]['company'],
               "segment": userPrincipalsResponse['accounts'][0]['segment'],
               "cddomain": userPrincipalsResponse['accounts'][0]['accountCdDomainId'],
               "usergroup": userPrincipalsResponse['streamerInfo']['userGroup'],
               "accesslevel":userPrincipalsResponse['streamerInfo']['accessLevel'],
               "authorized": "Y",
               "timestamp": int(tokenTimeStampAsMs),
               "appid": userPrincipalsResponse['streamerInfo']['appId'],
               "acl": userPrincipalsResponse['streamerInfo']['acl'] }


        login_request = {"requests": [{"service": "ADMIN",
                              "requestid": "0",  
                              "command": "LOGIN",
                              "qoslevel": "0", # express: 500ms
                              "account": userPrincipalsResponse['accounts'][0]['accountId'],
                              "source": userPrincipalsResponse['streamerInfo']['appId'],
                              "parameters": {"credential": urllib.parse.urlencode(credentials),
                                             "token": userPrincipalsResponse['streamerInfo']['token'],
                                             "version": "1.0"}}]}


        data_request= {"requests": [{"service": "QUOTE", 
                             "requestid": "2", 
                             "command": "SUBS", 
                             "account": userPrincipalsResponse['accounts'][0]['accountId'], 
                             "source": userPrincipalsResponse['streamerInfo']['appId'], 
                             "parameters": {"keys": tickersString,
                                            "fields": ("0,1,2,3,8" if not getOnlyLastPrice else "0,3")}}]}

        login_encoded = json.dumps(login_request)
        data_encoded = json.dumps(data_request)

        socketOpenURL = "wss://" + userPrincipalsResponse['streamerInfo']['streamerSocketUrl'] + "/ws"

        # Creating client object
        self.client = WebClient(self.sendDataPipe)
        
        self.loop = asyncio.get_event_loop()
        
        connectAttempts = 0
        prevConnectAttemptTime = None
        while connectAttempts < 5:
            print("beginning of TDA connect loop...")

            nowTime = datetime.datetime.now()
            if prevConnectAttemptTime != None:
                if nowTime - prevConnectAttemptTime > datetime.timedelta(minutes=1): # if the last attempt was long enough ago, reset attempts 
                    connectAttempts = 0
                else:
                    connectAttempts += 1
            prevConnectAttemptTime = nowTime

            # Start connection and get client connection protocol
            self.connection = self.loop.run_until_complete(self.client.connect(socketOpenURL))
            
            # Start listener and heartbeat 
            tasks = [asyncio.ensure_future(self.client.receiveMessage(self.connection)),
                    asyncio.ensure_future(self.client.sendMessage(login_encoded)),
                    asyncio.ensure_future(self.client.receiveMessage(self.connection)),
                    asyncio.ensure_future(self.client.sendMessage(data_encoded)),
                    asyncio.ensure_future(self.client.receiveMessage(self.connection))]

            self.loop.run_until_complete(asyncio.wait(tasks))

            print("end of TDA connect loop...")
            time.sleep(5)

    
def getPriceHistoryJson(ticker):
    endpoint = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/pricehistory"

    now_datetime = datetime.datetime.now()
    weekday = now_datetime.weekday()
    daysAgoToStartFrom = config.days_of_history_to_get
    if weekday == 6:
        #Sunday - get through Friday morning 
        daysAgoToStartFrom = daysAgoToStartFrom + 1
    elif weekday == 0:
        #Monday - get through Friday morning
        daysAgoToStartFrom = daysAgoToStartFrom + 2
    
    getFromDateTime = (now_datetime - datetime.timedelta(daysAgoToStartFrom)).replace(hour = 1, minute = 0, second = 0)
    
    #NOTE : if market is closed on a Monday, Tuesday won't get enough data

    startdate = int(getFromDateTime.timestamp()*1000.0)
    enddate = int(now_datetime.timestamp()*1000.0)

    print(TerminalStrings.SYS_MESSAGE + " getting " + ticker + " history for timestamp ", \
        startdate, \
        " to timestamp ", \
        enddate)

    params = {
        "apikey": TDA_auth_config.consumer_key,
        #"periodType": "day",
        #"period": 1, # 1 day of data
        "frequencyType": "minute",
        "frequency": 1,
        # "needExtendedHoursData": True,
        #"startDate": int((datetime.datetime.now() - datetime.timedelta(1)).timestamp()),
        #"endDate": int(time.time())
        "startDate": startdate,
        "endDate": enddate
    }

    headers = {'Authorization': auth.getAuthString(),}

    content = requests.get(url = endpoint, params = params, headers = headers)
    contentJson = content.json()

    contentJson[DataTransferStrings.SERVICE_KEY] = DataTransferStrings.PRICE_HISTORY_KEY

    return contentJson

        
# add price history for one ticker 
def addPriceHistory(ticker, pipe):
    contentJson = getPriceHistoryJson(ticker)

    if 'error' in contentJson.keys():
        print(TerminalStrings.ERROR + " error from TDAMeritrade.addPriceHistory on ticker \""+ticker+"\": \"" + str(contentJson['error'] + "\""))
    else: 
        # okay - add history to strategy for ticker 
        pipe.send(json.dumps(contentJson))


