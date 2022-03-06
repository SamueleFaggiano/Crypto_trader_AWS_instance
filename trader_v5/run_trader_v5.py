import logging
import datetime
from trading_tools import Trader
from telethon.sync import TelegramClient, events
from binance.client import Client


def main():

	# initialize object 'trader'
	trader = Trader()

	# initialize logging
	logging.basicConfig(filename='log_file.log', filemode='a', format='%(message)s', level=logging.INFO)

	# set initial parameters
	initial_support = float(input('Input initial support: '))
	trader.read_config_file("config.ini", initial_support)

	# initialize Binance client
	binance_client = Client(trader.api_key, trader.api_secret)

	# initialize telegram
	with TelegramClient(trader.username, trader.api_id, trader.api_hash) as client:
		client.send_message(entity=trader.username, message="Algorithm started!")
	print('Initialization: done!')
	
	# get current price
	price = trader.get_price()
	trader.check_if_above(price, logging)
	

	# start reading continuously
	while True:


		if trader.wait_5s():
			

			# read price and check if above
			try:
				price = trader.get_price()
			except:
				print('error in step 1')
				pass


			# if price passing support, then buy
			if trader.above is False and price > trader.support:

				# buy
				trader.buy(logging, price, binance_client)	
				
				# wait for profit
				while(trader.waiting):

					print(str(datetime.datetime.now())[:-7] + ' - waiting for profit. Actual price ' + str(price) + ' (profit at ' + str(trader.target) + ')')

					try:
						price = trader.get_price()
					except:
						print('error in step 2')
						pass

					# if profit is reached, then sell
					if price >= trader.target:
						trader.sell(logging, price, '+', binance_client)

					# if price drops, then sell
					if price <= trader.safety_net:
						trader.sell(logging, price, '-', binance_client)

			trader.check_if_above(price, logging)




if __name__ == '__main__':
	main()