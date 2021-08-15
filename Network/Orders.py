import DataManagement.Auth.AccountData as AccountData
import requests 
import DataManagement.Auth.auth as auth


def sendOrder(order_dict):
    # TODO / NOTE : this does not use JH2

    endpoint = "https://api.tdameritrade.com/v1/accounts/" + (AccountData.getAccountData()["AccountID"]) + "/orders"

    headers = {'Authorization': auth.getAuthString(),}

    content = requests.post(url = endpoint, json = order_dict, headers = headers)

    # TODO can we detect errors? it hated content.json() since it seemed to have no data 
    # TODO verify it made a trade ? - maybe just if it ever has a problem doing so. 

    # if content != None:
    #     contentJson = content.json()
    #     if 'error' in contentJson.keys():
    #         print(TerminalStrings.ERROR + " error from order: \"" + str(contentJson['error'] + "\""))


def sendBuyMarketOrder(ticker, quantity):
    order_dict = dict({
        "orderType": "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [{
            "instruction": "Buy",
            "quantity": int(quantity),
            "instrument": {
                "symbol": ticker,
                "assetType": "EQUITY"
            }
        }]
    })

    sendOrder(order_dict)
    


def sendSellMarketOrder(ticker, quantity):
    order_dict = dict({
        "orderType": "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [{
            "instruction": "Sell",
            "quantity": int(quantity),
            "instrument": {
                "symbol": ticker,
                "assetType": "EQUITY"
            }
        }]
    })

    sendOrder(order_dict)


