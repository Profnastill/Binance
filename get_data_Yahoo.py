'''Модуль для вытаскивания данных с классической биржи data_yahoo'''
import datetime

import numpy as np
import pandas as pd
import pandas_datareader as pdr

curent_day = datetime.datetime.today()
start_day = datetime.date.today() - datetime.timedelta(0)


def yhoo_data_taker(asset, day):
    end_day = start_day - datetime.timedelta(day)
    print(start_day)

    #day_set = pdr.get_data_yahoo(asset, start=end_day, end=start_day)
    try:
        day_set = pdr.get_data_yahoo(asset, start=end_day, end=start_day)

    except:
        return pd.DataFrame()  # Если не сработало то вернем пустой дата фрейм
    day_set.reset_index(inplace=True)
    day_set = day_set.rename({'Date': 'Open time'}, axis='columns')
    day_set['Open time']=pd.DatetimeIndex(day_set['Open time'])
    print(day_set)
    day_set=day_set.drop_duplicates(subset=["Open time"])
    return day_set


if __name__ == "__main__":
    pd.options.display.max_rows = 2500
    pd.options.display.max_columns = 100
    pd.options.display.expand_frame_repr = False


    end_day = start_day - datetime.timedelta(260)
    day_set = yhoo_data_taker("BZ=F",750)
    print(day_set[-20::])

