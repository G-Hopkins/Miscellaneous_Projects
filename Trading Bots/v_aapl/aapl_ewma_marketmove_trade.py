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

#Initialising windows
short_w = -3
long_w = -10

#Initialising of account 
#order = api.submit_order(symbol='AAPL', qty='1', side='buy', type='market', time_in_force='day')

#Function turns the sequential values into a list then into a df
def AAPL_trader(p, df):
    #waiting period
    time.sleep(1)
    #Web scraping
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    price= float(soup.find('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text)
    #df creation
    p.append(price)
    df = pd.DataFrame(p)
    df.columns = ['Price']
    df['Difference'] = df['Price'].diff()
    df['Short_mavg'] = df['Price'].iloc[short_w:].ewm(span=30).mean()
    df['Long_mavg'] = df['Price'].iloc[long_w:].ewm(span=30).mean()
    df['Mavg_diff'] = df['Short_mavg'] - df['Long_mavg']
    # FIND WAY TO SEE IF IT CAN TELL NO TRADES ARE PRESENT
    #if df['Mavg_diff'].iloc[-1] > 0 and api.list_positions() == []:
       # order = api.submit_order(symbol='AAPL', qty='1', side='buy', type='market', time_in_force='day')
    #elif df['Mavg_diff'].iloc[-1] < 0 and api.list_positions() == []:
        #order = api.submit_order(symbol='AAPL', qty='1', side='sell', type='market', time_in_force='day')

    #if api.list_positions == [] and df['Mavg_diff'].iloc[-1] > 0:
       # order = api.submit_order(symbol='AAPL', qty='1', side='buy', type='market', time_in_force='day')
    #elif api.list_positions == [] and df['Mavg_diff'].iloc[-1] < 0:
       # order = api.submit_order(symbol='AAPL', qty='1', side='sell', type='market', time_in_force='day')
    #elif api.list_positions == [] and df['Mavg_diff'].iloc[-1] == 0:
        #print('Wait for it...')
    if api.list_positions() == []:
        if df['Mavg_diff'].iloc[-1] == 0:
            print('Waiting...')
        if df['Mavg_diff'].iloc[-1] > 0:
            order = api.submit_order(symbol='AAPL', qty='2', side='buy', type='market', time_in_force='day')
        elif df['Mavg_diff'].iloc[-1] < 0:
            order = order = api.submit_order(symbol='AAPL', qty='2', side='sell', type='market', time_in_force='day')
    #elif df['Mavg_diff'].iloc[-1] == 0:
       # print('Waiting...')
    elif df['Mavg_diff'].iloc[-1] > 0 and float(api.get_position('AAPL').unrealized_intraday_pl) < 2 and float(api.get_position('AAPL').unrealized_intraday_pl) > -5:
        order = api.submit_order(symbol='AAPL', qty='2', side='buy', type='market', time_in_force='day')
    elif df['Mavg_diff'].iloc[-1] < 0 and float(api.get_position('AAPL').unrealized_intraday_pl) > -5 and float(api.get_position('AAPL').unrealized_intraday_pl) < 2:
        order = api.submit_order(symbol='AAPL', qty='2', side='sell', type='market', time_in_force='day')
    elif float(api.get_position('AAPL').unrealized_intraday_pl) > 2:
        api.close_all_positions()
        order = api.submit_order(symbol='AAPL', qty='2', side='buy', type='market', time_in_force='day')
    elif float(api.get_position('AAPL').unrealized_intraday_pl) < -5:
        api.close_all_positions()
        order = api.submit_order(symbol='AAPL', qty='2', side='buy', type='market', time_in_force='day') 
    return df.tail(1)

for _ in ' '*600: print(AAPL_trader(p,df))

def liquidate():
    time.sleep(1)
    if float(api.get_position('AAPL').unrealized_intraday_pl > 0):
        api.close_all_positions()
    else: 
        return 'Waiting...'

for _ in ' '*200: print(liquidate())
