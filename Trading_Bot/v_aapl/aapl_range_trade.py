import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import alpaca_trade_api as alpaca

#API info
key = '###'
sk = '###'
url = 'https://paper-api.alpaca.markets'
api = alpaca.REST(key, sk, url, api_version='v2')

#Initialising empty list
p = []
df = pd.DataFrame()
strike_list = [10000]

def AAPL_trader(p,df):
    time.sleep(3)
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    price= float(soup.find('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text)
    p.append(price)
    df = pd.DataFrame(p)
    df.columns = ['Price']
    df['Difference'] = df['Price'].diff()
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup2 = BeautifulSoup(response.text, 'lxml')
    min_p = float(soup2.find_all('tr', {'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[4].text[11:17])
    max_p = float(soup2.find_all('tr', {'class': 'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[4].text[19:26])
    factor = 0.997
    strike_buy_p = ((max_p + min_p) / 2 * factor)
    df['P - BP'] = price - strike_buy_p
    df.loc[df['P - BP'] < -1, 'Buy?'] = True
    df.loc[df['P - BP'] > 0, 'Buy?'] = False
    if df['Buy?'].iloc[-1] == True:
        order = api.submit_order(symbol='AAPL', qty='2', side='buy', type='market', time_in_force='day')
    df['Strike_Sell'] = price * 1.0005
    if df['Buy?'].iloc[-1] == True:
        strike_list.append(df['Strike_Sell'].iloc[-1])
    for x in strike_list:
        if x < price:
            strike_list.remove(x)
            api.order = api.submit_order(symbol='AAPL', qty='2', side='sell', type='market', time_in_force='day')
    return [df.tail(1), strike_list[-1]]

for _ in ' '*400: print(AAPL_trader(p,df))

def liquidate():
    time.sleep(1)
    if float(api.get_position('AAPL').unrealized_intraday_pl > 0):
        api.close_all_positions()
    else: 
        return 'Waiting...'

for _ in ' '*200: print(liquidate())
