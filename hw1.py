# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(start_date, end_date, equities, allocations):
    '''

    :param start_date: datetime object
    :param end_date: datetime object
    :param equities: list of stock symbols (strings)
    :param allocations: list of percent allocation for each stock (float, must add to 1.0)
    :return: standard deviation of daily returns, average daily return of portfolio, Sharpe ratio, cumulative return
    '''

    # We want closing prices
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between start and end dates
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)

    # Get data from Yahoo
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # We only need closing data (you can specify other keys for
    # other types of data, like 'high', 'low', 'open', etc.
    ls_keys = ['close']

    # Retrieve data
    ldf_data = c_dataobj.get_data(ldt_timestamps, equities, ls_keys)

    # Create dictionary with data using the keys specified above in ls_keys
    d_data = dict(zip(ls_keys, ldf_data))

    # Create numpy array of close prices.
    na_price = d_data['close'].values

    # Normalize prices according to first day
    na_normalized_price = na_price / na_price[0, :]

    # Weight each normalized price
    na_weighted = na_normalized_price * allocations

    # Value for each day (row-wise sum)
    na_values = na_weighted.copy().sum(axis=1)

    # Return for each day
    na_daily_returns = na_values.copy()
    tsu.returnize0(na_daily_returns)

    # Volatility (standard deviation) of daily returns
    std_dev = np.std(na_daily_returns)

    # Get average daily return
    avg_daily_return = np.mean(na_daily_returns)

    # Calculate Sharpe ratio
    number_of_trading_days = len(na_daily_returns)

    sharpe = np.sqrt(number_of_trading_days) * (avg_daily_return / std_dev)

    # Calculate cumulative daily return using formula
    # daily_cum_ret(t) = daily_cum_ret(t-1) * (1 + daily_ret(t))

    daily_cum_ret = np.zeros(number_of_trading_days)
    daily_cum_ret[0] = 1.0

    for i in np.arange(1, number_of_trading_days, 1):
        daily_cum_ret[i] = daily_cum_ret[i-1] * (1 + na_daily_returns[i])

    #print daily_cum_ret
    #print na_daily_returns
    #print sharpe
    #print std_dev
    #print avg_daily_return
    #print daily_cum_ret[number_of_trading_days-1]


    return std_dev, avg_daily_return, sharpe, daily_cum_ret[number_of_trading_days-1]




if __name__ == "__main__":

    #Test function
    start_date = dt.datetime(2011, 1, 1)
    end_date = dt.datetime(2011, 12, 31)

    equities = ['AAPL', 'GLD', 'GOOG', 'XOM']

    allocations = [0.4, 0.4, 0.0, 0.2]
    simulate(start_date, end_date, equities, allocations)

    optimum_allocation = []
    best_sharpe = 0.0
    best_cum = 0.0
    best_avg_daily_ret = 0.0

    for a1 in np.arange(0.0, 1.0, 0.1):
        for a2 in np.arange(0.0, 1.0, 0.1):
            for a3 in np.arange(0.0, 1.0, 0.1):
                for a4 in np.arange(0.0, 1.0, 0.1):
                    if a1 + a2 + a3 + a4 == 1.0:
                        alloc = [a1, a2, a3, a4]

                        vol, avg_daily_ret, sharpe, cum_ret = simulate(start_date, end_date, equities, alloc)

                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_cum = cum_ret
                            best_avg_daily_ret = avg_daily_ret
                            optimum_allocation = alloc

    print "Start Date: ", start_date
    print "End Date: ", end_date
    print "Symbols: ", equities
    print "Optimum Allocations: ", optimum_allocation
    print "Sharpe Ratio: ", best_sharpe
    print "Volatility (stddev of daily returns): ", vol
    print "Average Daily Return: ", best_avg_daily_ret
    print "Cumulative Return: ", best_cum







