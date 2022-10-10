 The strategy: 
	Enter the market if:
		The MACD.macd line crosses the MACD.signal line to the upside
		The Simple Moving Average has a negative direction in the last x periods (actual value below value x periods ago)
		Set a stop price x times the ATR value away from the close

 	If in the market:
 		Check if the current close has gone below the stop price. If yes, exit.
		If not, update the stop price if the new stop price would be higher than the current.

Backtest process:
	Rule of thumb: 500 data points per parameter
	There are 7 parameters so 7x500=3500 data points each of training set and test set. 
	30-min interval data as MACD is good for small change in price. ~233 days. ~8 months
	test set: 1 Jan 2022 - 4 may 2022
	training set: 1 Sep 2021 - 31 Dec 2021  
	The list of crypto currencies for backtest: LTCUSDT, XMRUSDT, ETHUSDT, ALGOUSDT, AVAXUSDT (list from old to new)
	The standard params are :
        	('macd1', 24),
        	('macd2', 52),
        	('macdsig', 18),
        	('atrperiod', 14),
        	('atrdist', 3.0),
        	('smaperiod', 30),
        	('dirperiod', 10),
