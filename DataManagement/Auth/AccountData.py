import config 
import json 

def getAccountData():
    with open(config.config_json_file) as jsonfile:
        data = json.load(jsonfile)

    return data 