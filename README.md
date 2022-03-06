# Crypto-trader built on an AWS EC2 instance
This project is about an automatic trader written in Python and able to run on an AWS instance.
As shown below, the algorithm uses the Binance API to read the BTC price in real time and set orders (BUY/SELL). Moreover, the software notifies the user through Telegram every time the algorithm buys or sells cryptocurrencies.
![](https://github.com/SamueleFaggiano/Crypto_trader_AWS_instance/blob/main/trader_v5/dataflow_schema.JPG)

The algorithm is trained on recognizing a specific pattern and in that case it sets an order. Previous studies showed that the pattern of interest brings positive profit in about 62% of the times. The pattern of interest happens when the price gets close to the support, and once it starts going up again, that's the moment in which the algorithm buys exploiting the price raise.

To run the program, it is neccessary to run "run_trader_v5.py" filling the information in the configuration file. In particular, the creation of Binance and Telegram keys is required to make the script run.

Lastly, the software not only notifies the user about orders, but it is also possible to stop and restart the program sending the "Start" and "Stop" messages through Telegram.

