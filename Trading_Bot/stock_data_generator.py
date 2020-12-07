from datetime import datetime, timedelta
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np

def stock(x):
    ''' Input stock symbol, returns CP, R, C. R, Volatility'''
    today = datetime.today().strftime('%Y-%m-%d')
    beginning_date = datetime.today() - timedelta(days=2*365)
    df= web.DataReader(x, 'yahoo', start=beginning_date, end=today)
    df['Difference'] = df['Close'] - df['Open']
    #CLOSING PRICE
    x1 = plt.figure(1)
    plt.plot(df.index, df['Close'])
    plt.title(str(x) + ' Closing Price')
    plt.xlabel('YEAR')
    plt.ylabel('CLOSE PRICE')
    x1.show()
    #DAILY LOG RETURNS
    df['Returns'] = np.log(df[['Adj Close']].pct_change()+1)
    df['Cum. Returns'] = (1+ df['Returns']).cumprod()
    x2 = plt.figure(2)
    df['Returns'].hist(bins=60)
    plt.title(str(x) +' Daily Log Returns')
    plt.xlabel('LOG RETURNS')
    plt.ylabel('FREQUENCY')
    x2.show()
    print(df['Returns'].describe())
    #CUM RETURNS
    x3 = plt.figure(3)
    plt.plot(df.index, df['Cum. Returns'])
    plt.title(str(x) +' Cum. Returns')
    plt.xlabel('YEAR')
    plt.ylabel('CUMALATIVE RETURNS')
    x3.show()
    #MOVING AVERAGE
    adj_close_px = df['Adj Close']
    moving_avg = adj_close_px.rolling(window=40).mean()
    print(moving_avg[-20:])
    #VOLATILITY
    vol = df['Returns'].rolling(25).std()
    x4 = plt.figure(4)
    plt.plot(df.index, vol)
    plt.title(str(x) +' Volatility')
    plt.xlabel('YEAR')
    plt.ylabel('STD')
    x4.show()
    input()

#e.g
print(stock('AAPL'))