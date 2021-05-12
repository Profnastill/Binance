'''Модуль для вытаскивания данных с классической биржи data_yahoo'''
import pandas as pd
import pandas_datareader as pdr
import datetime
import numpy as np
import plotly.graph_objects as go

curent_day=datetime.datetime.today()
start_day=datetime.date.today()-datetime.timedelta(1)

def yhoo_data_taker(asset, day, end_day=start_day):
   end_day = start_day - datetime.timedelta(day)
   print(start_day)
   try:
      day_set = pdr.get_data_yahoo(asset, start=end_day, end=start_day)
   except:
      return pd.DataFrame()#Если не сработало то вернем пустой дата фрейм

   day_set=day_set[::-1]
   day_set.reset_index(inplace=True)
   day_set=day_set.rename({'Date':'Open time'},axis='columns')
   return day_set


if __name__=="__main__":
   day_set=yhoo_data_taker("RUB=X",260)
   print(day_set)

