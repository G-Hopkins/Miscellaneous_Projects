import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import alpaca_trade_api as alpaca

#API info
key = '...'
sk = '...'
url = 'https://paper-api.alpaca.markets'
api = alpaca.REST(key, sk, url, api_version='v2')

#Initialising empty list
p = []
df = pd.DataFrame()

#Initialising windows
short_w = -20
long_w = -40

#Function turns the sequential values into a list then into a df
def AAPL_tracker(p, df):
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
    response=requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    price= float(soup.find('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'}).find('span').text)
    p.append(price)
    df = pd.DataFrame(p)
    df.columns = ['Price']
    df['Difference'] = df['Price'].diff()
    df['Short_mavg'] = df['Price'].iloc[short_w:].ewm(span=30).mean()
    df['Long_mavg'] = df['Price'].iloc[long_w:].ewm(span=30).mean()
    df['Mavg_diff'] = df['Short_mavg'] - df['Long_mavg']
    #waiting period
    time.sleep(1)
    if df['Mavg_diff'].iloc[-1] > 0 :
        order = api.submit_order(symbol='AAPL', qty='1', side='buy', type='market', time_in_force='day')
    elif df['Mavg_diff'].iloc[-1] < 0:
        order = api.submit_order(symbol='AAPL', qty='1', side='sell', type='market', time_in_force='day')
    return df.tail(1)

while True:
    print(AAPL_tracker(p,df))

#print(api.close_all_positions())