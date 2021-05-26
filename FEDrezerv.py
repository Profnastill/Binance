from fredapi import Fred
import pandas as pd
import os
import pandas_datareader.data as web
import pandas_datareader as pdr


api = 'YOUR API HERE'
os.environ["QUANDL_API_KEY"] = 'YOUR API HERE'
os.environ["TIINGO_API_KEY"] = 'YOUR API HERE'

fred = Fred(api_key=api)

# E/P
symbol = 'MULTPL/SP500_EARNINGS_YIELD_MONTH'
SP500_EARNINGS_YIELD_MONTH = web.DataReader(symbol, 'quandl', '1962-01-01', '2020-03-09')
# FED Funds Rate
FEDFUNDS = fred.get_series('FEDFUNDS', observation_start='1962-01-01', observation_end='2020-03-09')
# Baa Bonds Yield
BAA = fred.get_series('BAA', observation_start='1962-01-01', observation_end='2020-03-09')