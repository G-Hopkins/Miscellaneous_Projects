import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import alpaca_trade_api as alpaca

#API info
key = ''
sk = ''
url = 'https://paper-api.alpaca.markets'
api = alpaca.REST(key, sk, url, api_version='v2')

#Initialising empty list
p = []
df = pd.DataFrame()
strike_list = [10000]
stop_sell_list = [-10000]
TR = []

#Initialising windows
short_w = -6
long_w = -25

#Function turns the sequential values into a list then into a df
def AAPL_trader(p, df):
    #waiting period
    time.sleep(2)
    #Web scraping
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    price= float(soup.find('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text)
    p.append(price)
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup2 = BeautifulSoup(response.text, 'lxml')
    min_p = float(soup2.find_all('tr', {'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[4].text[11:17])
    max_p = float(soup2.find_all('tr', {'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[4].text[19:26])

    #Dataframe creation
    df = pd.DataFrame(p)
    df.columns = ['Price']
    df['Difference'] = df['Price'].diff()
    df['Short_mavg'] = df['Price'].iloc[short_w:].ewm(span=30).mean()
    df['Long_mavg'] = df['Price'].iloc[long_w:].ewm(span=30).mean()
    df['Mavg_diff'] = df['Short_mavg'] - df['Long_mavg']
    df['TR'] = max_p - min_p
    df['ATR'] = df['TR'].ewm(span=20).mean()
    df.loc[df['Mavg_diff'] > 0, 'Buy?'] = True
    df.loc[df['Mavg_diff'] < 0, 'Buy?'] = False
    df['Strike_Sell'] = price * 1.001
    df['Stop_Sell'] = price * 0.9995
    #Buy commands/ Stop-loss
    if df['Buy?'].iloc[-1] == True :
        order = api.submit_order(symbol='AAPL', qty='1', side='buy', type='market', time_in_force='day')
    if df['Buy?'].iloc[-1] == True:
        strike_list.append(df['Strike_Sell'].iloc[-1])
        stop_sell_list.append(df['Stop_Sell'].iloc[-1])
    
    #Tracking of orders
    for x in strike_list:
        if x < price:
            strike_list.remove(x)
            api.order = api.submit_order(symbol='AAPL', qty='1', side='sell', type='market', time_in_force='day')
    for x in stop_sell_list:
        if x > price:
            stop_sell_list.remove(x)
            api.order = api.submit_order(symbol='AAPL', qty='1', side='sell', type='market', time_in_force='day')
    return df.tail(1)

for _ in ' '*600: print(AAPL_trader(p,df))

def liquidate():
    time.sleep(1)
    if float(api.get_position('AAPL').unrealized_intraday_pl) > 0.5:
        api.close_all_positions()
    else: 
        return str(api.get_position('AAPL').unrealized_intraday_pl) + ' Waiting...'

for _ in ' '*200: print(liquidate())