import pandas as pd
#pd.set_option('display.max_columns', None)  # or 1000
#pd.set_option('display.max_rows', None)  # or 1000
#pd.set_option('display.max_colwidth', None)  # or 199

df = pd.read_csv('final_results.csv')
#df.sort_values(by=['profit'],inplace=True,ascending=False)

"""
df_XMRUSDT=df[df['symbol']=='XMRUSDT']
total_profit_vs_buy_hold=df_XMRUSDT['profit_vs_BuyHold'].sum()
total_profit=df_XMRUSDT['profit'].sum()
print('total profit: {:.2f}'.format(total_profit))
print('total profit vs buy hold strategy: {:.2f}'.format(total_profit_vs_buy_hold))
print(df_XMRUSDT)
"""

df_XMRUSDT=df[df['symbol']=='XMRUSDT']
total_profit_vs_buy_hold=df_XMRUSDT['profit_vs_BuyHold'].sum()
total_profit=df_XMRUSDT['profit'].sum()
print('total profit: {:.2f}'.format(total_profit))
print('total profit vs buy hold strategy: {:.2f}'.format(total_profit_vs_buy_hold))
print(df_XMRUSDT)