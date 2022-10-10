import csv
from binance.client import Client
from datetime import datetime
import sys
sys.path.append('/home/schrodinger/Desktop/work/python/Completed_codes/MACD/function')
import personal_function as pf

client = pf.Client()
"""
#30 min interval

start_date_training='1 Sep, 2021'
end_date_training='31 Dec, 2021'
start_date_test='1 Jan, 2022'
end_date_test='4 May, 2022'
symbol_list=['LTCUSDT','XMRUSDT','ETHUSDT','ALGOUSDT','AVAXUSDT']

for symbol in symbol_list:  
    csvfile = open('{}_training_set.csv'.format(symbol), 'w', newline='') 
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_30MINUTE, start_date_training, end_date_training)
    for candlestick in  candlesticks:
        #print(candlestick)
        candlestick[0] = int(candlestick[0]/1000)
        candlestick_writer.writerow(candlestick)
    csvfile.close()

    csvfile = open('{}_test_set.csv'.format(symbol), 'w', newline='') 
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_30MINUTE, start_date_test, end_date_test)
    for candlestick in  candlesticks:
        #print(candlestick)
        candlestick[0] = int(candlestick[0]/1000)
        candlestick_writer.writerow(candlestick)
    csvfile.close()
"""
#4 hour interval
start_date_training='30 Apr, 2020'
end_date_training='30 Apr, 2021'
start_date_test='1 May, 2021'
end_date_test='1 May, 2022'
symbol_list=['LTCUSDT','XMRUSDT','ETHUSDT','ALGOUSDT','AVAXUSDT']

for symbol in symbol_list:  
    csvfile = open('{}_4h_training_set.csv'.format(symbol), 'w', newline='') 
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_4HOUR, start_date_training, end_date_training)
    for candlestick in  candlesticks:
        #print(candlestick)
        candlestick[0] = int(candlestick[0]/1000)
        candlestick_writer.writerow(candlestick)
    csvfile.close()

    csvfile = open('{}_4h_test_set.csv'.format(symbol), 'w', newline='') 
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_4HOUR, start_date_test, end_date_test)
    for candlestick in  candlesticks:
        #print(candlestick)
        candlestick[0] = int(candlestick[0]/1000)
        candlestick_writer.writerow(candlestick)
    csvfile.close()