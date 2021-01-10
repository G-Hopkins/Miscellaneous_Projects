#Modern Portfolio Implementation to optimise weightings within a portfolio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
import pandas_datareader as dr

#Initialising tickers etc.
tickers=['AAPL', 'EOG', 'GOOGL', 'FB']
start_date = '2018-01-01'
end_date='2020-10-28'
currency = '$$$'

#Creation of Adj Close DF (Date is already index)
data = dr.DataReader(tickers, 'yahoo', start_date, end_date)
data = data['Adj Close']

#Checking for NaN and Dtype
#print(data.info())

#Price Movement over Time Visualisation
x1 = plt.figure(1)
for v in data.columns.values:
    plt.plot(data.index, data[v], label=v)
plt.legend()
plt.title('Price Movements over Time')
plt.ylabel(currency)
plt.xlabel('Time')

#Volatility 
volatility_data = data.pct_change()
x2 = plt.figure(2)
for v in volatility_data.columns.values:
    plt.plot(volatility_data.index, volatility_data[v], label=v)
plt.legend()
plt.title('Daily Returns over Time')
plt.ylabel('Daily Returns')
plt.xlabel('Time')

#Function to calculate annualised returns and volatility
def portfolio(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns*weights)*252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return std, returns

#Function to generate random portfolios
def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
    results = np.zeros((3, num_portfolios))
    weights_values = []
    for i in range(num_portfolios):
        #creation of array with sum 1
        weights = np.random.random(4)
        weights /= np.sum(weights)
        #appending of new array into the empty list
        weights_values.append(weights)
        #calculation of volatility and return for a set
        portfolio_std, portfolio_return = portfolio(weights, mean_returns, cov_matrix)
        #volatility assigned to empty field in results
        results[0,i] = portfolio_std
        #return
        results[1,i] = portfolio_return
        #Sharpe ratio
        results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std
    return results, weights_values

#Efficient Frontier and Sharpe Ratio Maximiser
def efficient_frontier(mean_returns, cov_matrix, num_portfolios, risk_free_rate):
    results, weights = random_portfolios(num_portfolios,mean_returns, cov_matrix, risk_free_rate)
    #find maximum Sharpe value index
    max_sharpe_idx = np.argmax(results[2])
    #return and std of maximum Sharpe ratio
    sdp, rp = results[0,max_sharpe_idx], results[1,max_sharpe_idx]
    #Dataframe of weightings for maximising sharpe ratio
    max_sharpe_allocation = pd.DataFrame(weights[max_sharpe_idx],index=data.columns,columns=['allocation'])
    #Conversion of weightings to %
    max_sharpe_allocation.allocation = [round(i*100,2)for i in max_sharpe_allocation.allocation]
    #Transposing of df
    max_sharpe_allocation = max_sharpe_allocation.T
    #finding minimum volatility index
    min_vol_idx = np.argmin(results[0])
    sdp_min, rp_min = results[0,min_vol_idx], results[1,min_vol_idx]
    min_vol_allocation = pd.DataFrame(weights[min_vol_idx],index=data.columns,columns=['allocation'])
    min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T
    
    print ("-"*80)
    print ("Maximum Sharpe Ratio Portfolio Allocation\n")
    print ("Annualised Return:", round(rp,2))
    print ("Annualised Volatility:", round(sdp,2))
    print ("\n")
    print (max_sharpe_allocation)
    print ("-"*80)
    print ("Minimum Volatility Portfolio Allocation\n")
    print ("Annualised Return:", round(rp_min,2))
    print ("Annualised Volatility:", round(sdp_min,2))
    print ("\n")
    print (min_vol_allocation)
    
    #Plotting of remaining points
    plt.figure(figsize=(10, 7))
    plt.scatter(results[0,:],results[1,:],c=results[2,:],cmap='coolwarm', marker='o', s=10, alpha=0.3)
    plt.colorbar()
    #Assining max Sharpe Ratio and lowest volatility with *'s
    plt.scatter(sdp,rp,marker='*',color='r',s=500, label='Maximum Sharpe ratio')
    plt.scatter(sdp_min,rp_min,marker='*',color='g',s=500, label='Minimum volatility')
    plt.title('Simulated Efficient Frontier for Portfolio Optimisation')
    plt.xlabel('Annualised Volatility')
    plt.ylabel('Annualised Returns')
    plt.legend(labelspacing=1.0)
    return plt.show()

#Inputs
returns = data.pct_change()
mean_returns = returns.mean()
cov_matrix = returns.cov()
num_portfolios = 20000
risk_free_rate = 0.09

print(efficient_frontier(mean_returns, cov_matrix, num_portfolios, risk_free_rate))