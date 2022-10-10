import websocket, json, pprint, talib
from binance.client import Client
from binance.enums import *
from datetime import datetime, timezone, timedelta
import telegram_send
import numpy as np
import sys
sys.path.append('/home/schrodinger/Desktop/work/python/Ongoing_projects/MACD_2/function')
import personal_function as pf



def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    #Set variable
    global time_zone,symbol,in_position,type,quantity
    global closes, highs, lows, closes
    global fastperiod, slowperiod, signalperiod, ATRperiod,smaperiod, dirperiod, direction, stop_price
    json_message = json.loads(message)
    #pprint.pprint(json_message)
    candle = json_message['k']
    time= json_message['E']
    is_candle_closed = candle['x']
    open_price= float(candle['o'])
    high_price=float(candle['h'])
    low_price=float(candle['l'])
    close_price = float(candle['c'])
    time=int(time/1000)
    time=(datetime.fromtimestamp(time,time_zone).strftime('%Y-%m-%d %H:%M:%S'))
    
    #Check candle closed
    if is_candle_closed:
        print("{} candle closed at {:.2f}".format(time,close_price))
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        np_closes=np.array(closes)
        np_highs=np.array(highs)
        np_lows=np.array(lows)
        with open("bot_results.csv", "a") as f:
            f.write("{},{:.2f},{:.2f},{:.2f},{:.2f}".format(time,open_price,high_price,low_price,close_price))
        
        #Calculate ATR
        if len(closes)>=(ATRperiod+1):
            ATR = talib.ATR(np_highs, np_lows, np_closes, timeperiod=ATRperiod)
            print("The last ATR is {:.2f}".format(ATR[-1]))
            with open("bot_results.csv", "a") as f:
                f.write(",{:.2f}".format(ATR[-1]))

            #Calculate SMA
            if len(closes)>= smaperiod:
                SMA=talib.SMA(np_closes, timeperiod=smaperiod)
                print("The last SMA is {:.2f}".format(SMA[-1]))
                with open("bot_results.csv", "a") as f:
                    f.write(",{:.2f}".format(SMA[-1]))
                #Calculate MACD
                if len(closes)>=(slowperiod+signalperiod-1):
                    macd, macdsignal, macdhist = talib.MACD(np_closes, \
                        fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
                    last_macd=macd[-1]
                    last_macdsignal=macdsignal[-1]
                    print("the current macd is {:.2f}".format(last_macd))
                    print("the current macd signal is {:.2f}".format(last_macdsignal))
                    with open("bot_results.csv", "a") as f:
                        f.write(",{:.2f},{:.2f}".format(last_macd, last_macdsignal))
                #else:
                #    with open("bot_results.csv", "a") as f:
                #        f.write(",,")
                    #Calculate direction
                    if len(SMA)>=(dirperiod+smaperiod):
                        if SMA[-1]>SMA[-dirperiod]:
                            print("Trend is up")
                            direction='Up'
                            with open("bot_results.csv", "a") as f:
                                f.write(", Up")

                        elif SMA[-1]<SMA[-dirperiod]:
                            direction='Down'
                            print("Trend is down")
                            with open("bot_results.csv", "a") as f:
                                f.write(", Down")
                        else:
                            direction='Horizontal'
                            print('Trend is horizontal')
                            with open("bot_results.csv", "a") as f:
                                f.write(", Horizontal") 

                    #SELL
                    if in_position:
                        if np_closes[-1]<stop_price:
                            in_position=False
                            print('Close price crosses below the stop price! Sell!')
                            with open("bot_results.csv", "a") as f:
                                f.write(",{:.2f}, SELL".format(stop_price))
                            order = client.create_order(symbol=symbol, side=SIDE_SELL, type=type, quantity=quantity)
                            time_tran=order['transactTime']
                            time_tran=int(time_tran/1000)
                            time_tran=(datetime.fromtimestamp(time_tran,time_zone).strftime('%Y-%m-%d %H:%M:%S'))
                            side=order['side']
                            qty=float(order['fills'][0]['qty'])
                            symbol=order['symbol']
                            price=float(order['fills'][0]['price'])
                            telegram_send.send(messages=['MACD_bot {} {} {:.2f} {} at {:.2f} USDT'.format(time_tran,side,qty,symbol,price)]) 
                            print('{} {} {:.2f} {} at {:.2f} USDT'.format(time_tran,side,qty,symbol,price))
                        else: 
                            stop_price=np_closes[-1]-ATR[-1]*ATRdist
                            with open("bot_results.csv", "a") as f:
                                f.write(",{:.2f}, HOLD".format(stop_price))

                    #Buy
                    if macd[-1]>macdsignal[-1] and direction=='Down':
                        if not in_position:
                            print('MACD crosses above its signal line and the direction of SMA is negative! Buy!')
                            in_position=True
                            stop_price=np_closes[-1]-ATR[-1]*ATRdist
                            with open("bot_results.csv", "a") as f:
                                f.write(",{:.2f}, BUY".format(stop_price))
                            order = client.create_order(symbol=symbol, side=SIDE_BUY, type=type, quantity=quantity)
                            time_tran=order['transactTime']
                            time_tran=int(time_tran/1000)
                            time_tran=(datetime.fromtimestamp(time_tran,time_zone).strftime('%Y-%m-%d %H:%M:%S'))
                            side=order['side']
                            qty=float(order['fills'][0]['qty'])
                            symbol=order['symbol']
                            price=float(order['fills'][0]['price'])
                            telegram_send.send(messages=['MACD_bot {} {} {:.2f} {} at {:.2f} USDT'.format(time_tran,side,qty,symbol,price)]) 
                            print('{} {} {:.2f} {} at {:.2f} USDT'.format(time_tran,side,qty,symbol,price))
                        else:
                            print('Conditions to take positions are satisfied but we are already in the market.')                      

        #Close the row
        with open("bot_results.csv", "a") as f:
            f.write('\n') 

#main
#variables


type=ORDER_TYPE_MARKET
quantity=1
symbol = 'LUNAUSDT'
time_zone = timezone(timedelta(hours=8))
in_position = False
SOCKET = "wss://stream.binance.com:9443/ws/lunausdt@kline_1m"

opens=[]
highs=[]
lows=[]
closes = []

fastperiod=4
slowperiod=10
signalperiod=4
ATRperiod=4
ATRdist=1
smaperiod=9
dirperiod=7
direction='No'
stop_price=0

client=pf.client()

telegram_send.send(messages=['Hello, MACD strategy is running'])
open("bot_results.csv", "w").close()
with open("bot_results.csv", "a") as f:
    f.write("Time,Open,High,Low,Close,ATR,SMA,MACD,MACD Signal,Direction,Stop Price,Buy/Hold/Sell\n")     

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
