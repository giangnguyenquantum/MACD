from glob import glob
import backtrader as bt
import datetime
import sys
import backtrader.analyzers as btanalyzers

def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=50, tight=True, use=None, file_path = '', **kwargs):

        from backtrader import plot
        if cerebro.p.oldsync:
            plotter = plot.Plot_OldSync(**kwargs)
        else:
            plotter = plot.Plot(**kwargs)

        figs = []
        for stratlist in cerebro.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 10,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use,width=1600, height=900,dpi=2000)
                figs.append(rfig)

        for fig in figs:
            for f in fig:
                f.savefig(file_path, bbox_inches='tight')
        return figs

class MACDStrategy(bt.Strategy):
    params = (
    # Standard MACD Parameters
        ('macd1', 24),
        ('macd2', 52),
        ('macdsig', 18),
        ('atrperiod', 14),
        ('atrdist', 3.0),
        ('smaperiod', 30),
        ('dirperiod', 10),
    )
    def log(self, txt, dt=None):
        #Print function
        dt = dt or self.datas[0].datetime.datetime(0)
        with open('backtest_results.txt', 'a') as f:
            f.write('%s, %s' % (dt.isoformat(), txt))
            f.write('\n')
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        global profit
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        profit=profit+trade.pnlcomm
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def __init__(self):
        # Initializing...
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        #self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)        
        self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
        self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def next(self):
        global cash_percentage
        #self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        
        if not self.position:
            if self.macd.macd > self.macd.signal and self.smadir < 0.0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.size=self.broker.cash*cash_percentage/self.data.close
                self.order=self.buy(size=self.size)
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist

        else:
            pclose = self.data.close[0]
            pstop = self.pstop
            if pclose < pstop:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order=self.close()
            else:
                pdist = self.atr[0] * self.p.atrdist
                # Update only if greater than
                self.pstop = max(pstop, pclose - pdist)


class BuyHoldStrategy(bt.Strategy):

    def next(self):
        global cash_percentage
        if self.position.size==0:
            self.size=self.broker.cash*cash_percentage/self.data.close
            self.order=self.buy(size=self.size)


#variables
#initilize variable:
symbol=sys.argv[1]
macd1=int(sys.argv[2])
macd2=int(sys.argv[3])
macdsig=int(sys.argv[4])
atrperiod=int(sys.argv[5])
atrdist=int(sys.argv[6])
smaperiod=int(sys.argv[7])
dirperiod=int(sys.argv[8])

print('symbol: {}'.format(symbol))
print('fast_MACD: {}'.format(macd1))
print('slow_MACD: {}'.format(macd2))
print('signal_MACD: {}'.format(macdsig))
print('atr_period: {}'.format(atrperiod))
print('atr_distance: {}'.format(atrdist))
print('sma_period: {}'.format(smaperiod))
print('direction_period: {}'.format(dirperiod))

#For cerebro
cash_percentage=0.95
data_name='/home/schrodinger/Desktop/work/python/Completed_codes/MACD/data/{}_4h_test_set.csv'.format(symbol)
slip_perc=0.005 
set_cash=1000 
set_commission=0.001
profit=0
data = bt.feeds.GenericCSVData(
    dataname=data_name, 
    dtformat=2, 
    #compression=240, 
    timeframe=bt.TimeFrame.Minutes,
    )

#main
#initialize cerebro MACD
cerebro = bt.Cerebro()
cerebro.addstrategy(MACDStrategy,
macd1=macd1,
macd2=macd2,
macdsig=macdsig,
atrperiod=atrperiod,
atrdist=atrdist,
smaperiod=smaperiod,
dirperiod=dirperiod
)

cerebro.broker = bt.brokers.BackBroker(slip_perc=slip_perc,slip_open=True,slip_match=True, slip_out=False)
cerebro.adddata(data)
cerebro.broker.setcash(set_cash)
cerebro.broker.setcommission(commission=set_commission)

cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe',\
    timeframe=bt.TimeFrame.Days, compression=1, factor=365,annualize =True)

cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')

cerebro.addanalyzer(btanalyzers.TimeDrawDown, _name='drawdownduration',\
    timeframe=bt.TimeFrame.Days, compression=1)


#cerebro.run()
with open('backtest_results.txt', 'a') as f:
    f.write('{},{},{},{},{},{},{},{}'.format(symbol,macd1,macd2,macdsig,atrperiod,atrdist,smaperiod,dirperiod))
    f.write("The commission is {}% and the slippage is {}%.\n".format(set_commission*100,slip_perc*100))
    f.write('Starting Portfolio Value: %.2f\n' % cerebro.broker.getvalue())

strat = cerebro.run()
sharpe= strat[0].analyzers.mysharpe.get_analysis()
drawdown=strat[0].analyzers.drawdown.get_analysis()
drawdownduration=strat[0].analyzers.drawdownduration.get_analysis()

print('Final MACD Portfolio Value: %.2f\n' % cerebro.broker.getvalue())
print('profit MACD: {}'.format(profit))
print('DONE')
#note that we can see the difference between the final and the intial portfolio is not equal
#to the overall profit. It is because the final executation is a BUY. 
#so the final portfolio is cash+ the price of the stock of the last price - the last commission fee.
#cerebro.plot()
saveplots(cerebro, file_path = 'figure/{}_{}_{}_{}_{}_{}_{}_{}.png'.format(symbol,macd1,macd2,macdsig,atrperiod,atrdist,smaperiod,dirperiod))

#initialize cerebro BuyHold
cerebro2 = bt.Cerebro()
cerebro2.addstrategy(BuyHoldStrategy)

cerebro2.adddata(data)
cerebro2.broker.setcash(set_cash)
cerebro2.run()
print('Final Portfolio Value: %.2f\n' % cerebro2.broker.getvalue())
print('DONE')
compare_BuyHold=cerebro.broker.getvalue()-cerebro2.broker.getvalue()
with open('backtest_results.txt', 'a') as f:
    f.write('Final Portfolio Value: %.2f\n' % cerebro.broker.getvalue())
    f.write('The overall profit: %.2f\n' %profit)
    f.write('The profit versus Buy and Hold strategy: %.2f\n' %compare_BuyHold)
with open('final_results.csv','a') as f:
    f.write('{},{},{},{},{},{},{},{},{:.2f},{:.2f},{:.2f},{},{:.2f}\n'\
        .format(symbol,macd1,macd2,macdsig,atrperiod,atrdist,smaperiod,\
            dirperiod,profit,sharpe['sharperatio'],drawdown['max']['drawdown'],drawdown['max']['len'],compare_BuyHold))


