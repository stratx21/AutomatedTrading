from selenium import webdriver
from tda.auth import easy_client, client_from_login_flow, client_from_manual_flow
from tda.client import Client
from tda.streaming import StreamClient
from tda.orders.generic import OrderBuilder
from tda.orders.common import OrderType, EquityInstruction, Duration, Session, OrderStrategyType 
from config import consumer_key, callback_url, acct

import asyncio
import json


class TDAClient:
    stream_client = None 
    token_path = "token.config"
    #client_from_login_flow(webdriver, consumer_key, callback_url, token_path, redirect_wait_time_seconds=0.1, max_waits=3000, asyncio=False, token_write_func=None)
    #client_from_manual_flow(consumer_key, callback_url, token_path, asyncio=False, token_write_func=None)
    
    
    # , "expires_at": "2021-05-22 13:44:37.375473"
    
    def __init__(self):
        client = easy_client(
                api_key=consumer_key,
                redirect_uri=callback_url,
                token_path=self.token_path)
        self.stream_client = StreamClient(client, account_id=acct)
        
        # await stream_client.level_one_equity_subs("LABU,GUSH")
        
        builder = OrderBuilder()
        builder.set_order_type(OrderType.MARKET)
        builder.add_equity_leg(EquityInstruction.BUY, "LABU", 1)
        builder.set_duration(Duration.DAY)
        builder.set_order_strategy_type(OrderStrategyType.SINGLE)
        builder.set_session(Session.NORMAL)
        
        print("res: " , client.place_order(acct, builder))
            
        # self.startReadStream()
        
        
    async def read_stream(self):
        await self.stream_client.login()
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        # Always add handlers before subscribing because many streams start sending
        # data immediately after success, and messages with no handlers are dropped.
        self.stream_client.add_nasdaq_book_handler(
                lambda msg: print(json.dumps(msg, indent=4)))
        await self.stream_client.level_one_equity_subs("LABU,GUSH") # TODO update with only fields wanted 

        while True:
                await self.stream_client.handle_message()

#     def startReadStream(self):
#         asyncio.run(self.read_stream())



clnt = TDAClient()
asyncio.run(clnt.read_stream())
print("GOT HERE ") 