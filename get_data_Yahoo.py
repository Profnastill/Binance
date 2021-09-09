'''Модуль для вытаскивания данных с классической биржи data_yahoo'''
import datetime

import numpy as np
import pandas as pd
import pandas_datareader as pdr

curent_day = datetime.datetime.today()
start_day = datetime.date.today() - datetime.timedelta(0)


def yhoo_data_taker(asset, day, end_day=start_day):
    end_day = start_day - datetime.timedelta(day)
    print(start_day)

    #day_set = pdr.get_data_yahoo(asset, start=end_day, end=start_day)
    try:
        day_set = pdr.get_data_yahoo(asset, start=end_day, end=start_day)

    except:
        return pd.DataFrame()  # Если не сработало то вернем пустой дата фрейм
    print(day_set)
    # day_set=day_set[::1]
    day_set.reset_index(inplace=True)
    day_set = day_set.rename({'Date': 'Open time'}, axis='columns')
    PATTERN_IN = "%Y-%m-%d"
    # day_set['Open time']=pd.to_datetime(day_set['Open time'].values,format=PATTERN_IN)
    day_set['Open time'] = day_set['Open time'].apply(lambda x: (x.to_pydatetime()))

    return day_set


if __name__ == "__main__":
    end_day = start_day - datetime.timedelta(260)
    day_set = yhoo_data_taker("RUB=X", 260)
    print(day_set)
   # day_set["Open time"] = day_set["Open time"].tz_localize('UTC')
    '''''''''
    print(day_set["Open time"])
    day_set["Open time"]=day_set["Open time"].apply(lambda x: str(x).split("-"))

    print(day_set["Open time"])
    day_set["Open time"]=day_set["Open time"].apply(datetime.date())
    #day_set["Open time"] = day_set["Open time"].apply(lambda x: datetime.datetime.strptime(str(x).split("-"),"%Y-%m-%d"))
'''''
    day = day_set[["Open time"]][-1::].values[0][0]

    print(day)
    print(type(day), type(end_day))
    # print(type(datetime.timedelta(260)))

    day=pd.Timestamp(day).to_pydatetime()
    print(day)

    day = day + datetime.timedelta(days=260)

    print(day)
    # print((day_set,np.datetime64(start_day)))

    # print(day_set.loc[:,"Open time"])
    # day_set.loc[:,"Close"]=day_set["Close"].astype(datetime)
    print(((start_day) in day_set.loc[:, "Open time"]))
    # print((76 in day_set.loc[:, "Close"]))
    print((np.datetime64(start_day) in day_set["Open time"]))
    print((np.datetime64(start_day) == day_set["Open time"][-1::]))
    # day_set.query("'Open time' == @start_day")
    # day_set=day_set.query("'Open time' == @start_day")

    print(day_set.dtypes)
    # a= day_set["Open time"].eq(pd.to_datetime(start_day)).any()
    a = day_set.query("`Open time` == @start_day")
    a = not day_set.query('"Open time" == @start_day').empty
    print(a)
