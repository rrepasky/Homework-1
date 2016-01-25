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
    na_returns = na_values.copy()
    tsu.returnize0(na_returns)

    # Volatility (standard deviation) of daily returns
    std_dev = np.std(na_returns)

    # Get average daily return
    avg_return = np.mean(na_returns)

    # Calculate Sharpe ratio
    sharpe = np.sqrt(252) * (avg_return / std_dev)

    print sharpe

    print std_dev

    print avg_return




if __name__ == "__main__":

    #Test function
    start_date = dt.datetime(2011, 1, 1)
    end_date = dt.datetime(2011, 12, 31)

	#Data to verify proper implementation
    equities = ['AAPL', 'GLD', 'GOOG', 'XOM']
    allocations = [0.4, 0.4, 0.0, 0.2]

    simulate(start_date, end_date, equities, allocations)





