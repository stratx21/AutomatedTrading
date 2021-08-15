import time

from multiprocessing import Process

from DataManagement.Auth.authTD import authentication, access_token
import json 
import config
import datetime 
import dateutil
import Terminal.TerminalStrings as TerminalStrings
import config.TDA_auth_config as TDA_auth_config

tokenUpdateProcess = None 


def init(isJH2 = False):

    with open(config.getTokenConfigFile(isJH2)) as jsontokenfile: 
        currentToken = json.load(jsontokenfile)

    beforeAuthNow = datetime.datetime.now()
    expires = dateutil.parser.parse(currentToken['expires_at'])

    minutesTillExpires = (expires - beforeAuthNow).seconds / 60

    # print("now: ", str(beforeAuthNow), "diff: ", minutesTillExpires)

    if (beforeAuthNow > expires):
        print(TerminalStrings.SYS_MESSAGE + " updating access token in init...")
        #expired or going to expire in a few minutes - get new token 
        runUpdateToken(isJH2)
        minutesTillExpires = config.refresh_token_minutes
    else: 
        print(TerminalStrings.SYS_MESSAGE + " current access token expires at: " + str(expires))

    #start auto-updater
    global tokenUpdateProcess
    tokenUpdateProcess = tokenUpdateProcess = Process(target = runUpdateProcessLoop, args = (minutesTillExpires, isJH2))
    tokenUpdateProcess.start()


def updateRefreshToken(isJH2 = False):
    # run chrome auth 
    auth = authentication(TDA_auth_config.client_id, config.callback_url) # blocks until done 
    
    # access_token = auth["access_token"]
    # refresh_token = auth["refresh_token"]
    # token_type = auth["token_type"]
    # authString = token_type +" "+ access_token


    now = datetime.datetime.now()
    expires = now + datetime.timedelta(minutes = config.refresh_token_minutes) # add delta time 
    auth['expires_at'] = str(expires)
    refreshExpires = now + datetime.timedelta(days = config.refresh_token_expires_days) # add delta time
    auth['refresh_expires_at'] = str(refreshExpires)

    with open(config.getTokenConfigFile(isJH2), 'w') as file:
        json.dump(auth, file)

    print(TerminalStrings.SYS_MESSAGE + " new refresh token and access token retrieved and saved. Access token expires at: " + str(expires) + ", refresh token expires at: " + str(refreshExpires))

def getRefreshTokenExpireTime(isJH2 = False):
    with open(config.getTokenConfigFile(isJH2)) as jsontokenfile: 
        currentToken = json.load(jsontokenfile)
    
    return currentToken["refresh_expires_at"]


# get most recent auth token from the file 
def getAuthString(isJH2 = False):
    with open(config.getTokenConfigFile(isJH2)) as jsontokenfile: 
        currentToken = json.load(jsontokenfile)
    
    return currentToken["token_type"] + " " + currentToken["access_token"]
    
def getRefreshTokenString(isJH2 = False):
    with open(config.getTokenConfigFile(isJH2)) as jsontokenfile: 
        currentToken = json.load(jsontokenfile)
    
    return currentToken["refresh_token"]

def runUpdateToken(isJH2 = False):
    
    
    refreshTokenString = getRefreshTokenString()

    auth = access_token(refreshTokenString, TDA_auth_config.consumer_key)

    # add time it expires minus 5 minutes: 
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(minutes = config.refresh_token_minutes) # add delta time 
    auth['expires_at'] = str(expires)
    auth['refresh_token'] = refreshTokenString
    auth['refresh_expires_at'] = str(getRefreshTokenExpireTime())

    # write info to file: 
    with open(config.getTokenConfigFile(isJH2), 'w') as file:
        json.dump(auth, file)

    print("\n"+TerminalStrings.SYS_MESSAGE + " new access token retrieved and saved. Expires at: " + str(expires))



def runUpdateProcessLoop(startingMinutes, isJH2):
    expiresInMinutes = startingMinutes
    while True:
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(minutes = expiresInMinutes) 
        expiresInMinutes = config.refresh_token_minutes
        # this runs within its own process - for the very
        # first update it needs to block. This is the updater 
        # for after the init. Thus update at the end 

        #this should never run, unless expiresInMinutes is negative from initial input from init 
        if expires < now:
            print(TerminalStrings.ERROR + " auth.runUpdateProcessLoop error; expires not < now. expires: ", str(expires), " now: ", str(now))

        time.sleep((expires - now).total_seconds())

        #now run the update: 
        runUpdateToken(isJH2)


