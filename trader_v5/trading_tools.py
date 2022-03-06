import configparser
import pandas as pd
import numpy as np
import urllib.request, json
import datetime
import logging
#import time
from telethon.sync import TelegramClient, events
from binance.exceptions import BinanceAPIException, BinanceOrderException


class Trader:

	def __init__(self):
		self.df_support = None
		self.support = None
		self.total_lenght = None
		self.offset = None
		self.upper_level = None
		self.gain = None
		self.above = None
		self.above_prev = True
		self.waiting = False
		self.target = None
		self.safety_net = None
		self.api_id = None
		self.api_hash = None
		self.phone = None
		self.username = None
		self.last = '0'
		self.api_key = None
		self.api_secret = None


	def read_config_file(self, name, initial_support):
		config = configparser.ConfigParser()
		config.read(name)
		self.total_lenght = int(config['Binance']['total_lenght'])
		self.offset = int(config['Binance']['offset'])
		self.upper_level = float(config['Binance']['upper_level'])
		self.gain = float(config['Binance']['gain'])
		self.df_support = pd.DataFrame(np.full(self.total_lenght, initial_support), columns=['support_history'])
		self.api_id = int(config['Telegram']['api_id'])
		self.api_hash = str(config['Telegram']['api_hash'])
		self.phone = config['Telegram']['phone']
		self.username = config['Telegram']['username']
		self.api_key = str(config['Binance']['api_key'])
		self.api_secret = str(config['Binance']['api_secret'])


	def wait_5s(self):
		if (str(datetime.datetime.now())[-8] == '0' or str(datetime.datetime.now())[-8] == '5') and np.abs(int(str(datetime.datetime.now())[-8])-int(self.last)) > 4:
			self.last = str(datetime.datetime.now())[-8]
			return True
		else:
			False


	def get_price(self):

		with urllib.request.urlopen("https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR") as url:
			data = json.loads(url.read().decode())
		price = float(data['price'])

		if str(datetime.datetime.now())[17:19] == '00':
			self.df_support = self.df_support.shift(periods=1)
			self.df_support.iloc[0,0] = price

		self.support = self.df_support.iloc[self.offset:, 0].min() * (self.upper_level/100+1)
		self.safety_net = self.df_support.iloc[self.offset:, 0].min()
		
		return price


	def check_if_above(self, price, logging):

		if price > self.support:
			self.above = True
			print(str(datetime.datetime.now())[:-7] + ' - read real time price: ' + str(price) + ' (support ' + str(self.support) + ')')

		else:
			self.above = False
			print(str(datetime.datetime.now())[:-7] + '- below support: ', self.support, '(actual price', price, ')')
			if self.above_prev == True:
				logging.info(str(datetime.datetime.now())[:-7] + ' - Got below the support ' + str(self.support) + ', current price ' + str(price))

		self.above_prev=self.above


	def buy(self, logging, price, binance_client):

		eur = binance_client.get_asset_balance(asset='EUR')['free']

		try:
			buy_order_limit = binance_client.create_order(
			    symbol='BTCEUR',
			    side='BUY',
			    type='LIMIT', 
			    timeInForce='GTC',
			    quantity=round(float(eur)/float(price),5),
			    price=price+10)
		except BinanceAPIException as e:
		    print(e)
		except BinanceOrderException as e:
		    print(e)

		self.waiting = True
		self.target = price * (self.gain/100+1)

		logging.info(str(datetime.datetime.now())[:-7] + ' - BUY: ' + str(price))
		with TelegramClient(self.username, self.api_id, self.api_hash) as client:
			client.send_message(entity=self.username, message=str(datetime.datetime.now())[:-7] + ' -> BUY: ' + str(price))


	def sell(self, logging, price, sign, binance_client):

		if sign == '+':
			sell_price = price+10
		else:
			sell_price = price-10

		btc = binance_client.get_asset_balance(asset='BTC')['free']

		try:
			buy_order_limit = binance_client.create_order(
			    symbol='BTCEUR',
			    side='SELL',
			    type='LIMIT',  
			    timeInForce='GTC',
			    quantity=round(float(btc),5),
			    price=sell_price)
		except BinanceAPIException as e:
		    print(e)
		except BinanceOrderException as e:
		    print(e)

		self.waiting = False

		logging.info(str(datetime.datetime.now())[:-7] + ' - SELL: ' + str(price))
		with TelegramClient(self.username, self.api_id, self.api_hash) as client:
			client.send_message(entity=self.username, message=str(datetime.datetime.now())[:-7] + ' -> SELL: ' + str(price) + '(' + sign + ')')

