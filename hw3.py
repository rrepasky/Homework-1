'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
'''

import sys
import csv
import operator

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Event is when stock initially drops below $5.00

            f_actual_close_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_actual_close_yest = df_close[s_sym].ix[ldt_timestamps[i-1]]

            if f_actual_close_today < 10.0 and f_actual_close_yest >= 10.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

            # Calculating the returns for this timestamp
            #f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            #f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            #f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            #if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
            #    df_events[s_sym].ix[ldt_timestamps[i]] = 1

    #return df_events

def event_profiler(ldt_timestamps, symbols_source):
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(symbols_source)
    ls_symbols.append('SPY')

    # Get actual close data
    ls_keys = ['close', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Remove NAN data
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Find events
    df_events = find_events(ls_symbols, d_data)

    report_name = "HW2_" + symbols_source + "_Event_Report" + ".pdf"

    print "Creating report " + report_name

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename=report_name, b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

def get_orders(orders_csv, ls_symbols, ls_data):
    s_symbols = set()

    reader = csv.reader(open(orders_csv, 'rU'), delimiter=',')

    for row in reader:
        s_symbols.add(row[3])
        ls_data.append([row[0], row[1], row[2], row[3], row[4], row[5]])

    ls_data.sort(key=lambda x:(x[0],x[1],x[2]))

    ls_symbols = list(s_symbols)

def get_market_data(ls_symbols, ls_data, d_data):

    # Set up date range

    last_row = len(ls_data) - 1
    dt_start = dt.datetime(int(ls_data[0][0]), int(ls_data[0][1]), int(ls_data[0][2]))
    dt_end = dt.datetime(int(ls_data[last_row][0]), int(ls_data[last_row][1]), int(ls_data[last_row][2]))

    # Get market data

    databoj = da.DataAccess('Yahoo')
    ls_keys = ['close', 'actual_close']
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    ldf_data = databoj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))


def marketsim(starting_cash, orders_csv, values_csv):

    ls_symbols = list()
    ls_data = list()
    d_data = dict()

    get_orders(orders_csv, ls_symbols, ls_data)

    get_market_data(ls_symbols, ls_data, d_data)

    print ls_data[0][0]
    #print s_symbols
    #print ls_data
    print d_data

if __name__ == '__main__':

    # Get command line args
    starting_cash = sys.argv[1]
    orders_csv = sys.argv[2]
    values_csv = sys.argv[3]

    print starting_cash
    print orders_csv
    print values_csv

    marketsim(starting_cash, orders_csv, values_csv)

    #dt_start = dt.datetime(2008, 1, 1)
    #dt_end = dt.datetime(2009, 12, 31)
    #ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    # Symbols from S&P 2008
    #event_profiler(ldt_timestamps, 'sp5002008')

    # Symbols from S&P 2012
    #event_profiler(ldt_timestamps, 'sp5002012')

