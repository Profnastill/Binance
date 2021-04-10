# Программа находит коэффцииент шарпа и сортино одновременно
import keys


import binance
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import plotly.graph_objects as go
import datetime


from binance.client import Client
import urllib3
import json
import time


pd.options.display.max_rows=10
pd.options.display.max_columns=10
pd.options.display.expand_frame_repr = False
urllib3.disable_warnings()




#API_key = "New_key"
API_key = keys.API_key
API_Secret = keys.API_Secret

converter = lambda x : x*2 if x < 11 else (x*3 if x < 22 else x)


client = Client(API_key, API_Secret)
current_time=client.get_server_time()
print("время сервера",current_time['serverTime'])

time_dd_format=time.ctime(current_time['serverTime']/1000)
print("время сервера",time_dd_format)




#print (client)
#client = Client(API_key, API_Secret, {"verify": False, "timeout": 20})
try:
    info = client.get_account()
except binance.client.BinanceAPIException as e:
    print (e.status_code)
    print (e.message)

#print (info)
usd_rub=float(client.get_avg_price(symbol="USDTRUB")["price"])#Стоимость доллара к рублю
bnb_rub=float(client.get_avg_price(symbol="BNBRUB")["price"])
#print (usd_rub)

status = client.get_account_status()
#print (status)
#balance = client.get_deposit_history

balance=client.get_account()['balances']
#print(balance)
table=pd.DataFrame(balance)
table['free']=table['free'].apply(lambda x: float(x))

selection_usdt = ((table.asset == "USDT"))
volume_usdt = table[selection_usdt]['free'].values
print(volume_usdt)
table = table[~selection_usdt]
table_base=table.copy(deep=True)# Базовая таблица для работы модулей аналитики
table=table.query('free > 0')

print("--"*10)
print (table)


def coint_info(asset):
    client.get_all_coins_info()
    client.get_al


def func_2(asset):
    "Вытаскиваем стоимость по позиции"
    x=asset
    val1,val2 = 0,0
    try:
        val1=float(client.get_avg_price(symbol=x + 'USDT')["price"])
    except:
        val2=float(client.get_avg_price(symbol=x + 'BNB')["price"])
        val1=None
    return pd.Series([val1,val2])

def fun_1(table):
    'функция нахождения баланса'
    table[['USDT','BNB']]=table['asset'].apply(func_2)
    table['USDT']=table['USDT']*table['free']
    table['BNB']=table['BNB']*table['free']
    suum_usdt=table['USDT'].sum()
    table['% balance']=table['USDT']/(suum_usdt+volume_usdt)*100
    table['RUB_cost']=table['USDT'].apply(lambda x: x*usd_rub)
    #table['RUB_cost']=table['BNB'].apply(lambda x: x*bnb_rub)
    table=table.reset_index(drop=True)
    print (round(table,1))
    print (f"стоимость портфеля в долларах {round(suum_usdt)}$",
    print (f"активы в долларах {volume_usdt[0].round()}"))
    return table

def write_json(data):
    with open(r'C:\Users\Давид\PycharmProjects\Binance\data.json', 'w') as f:json.dump(data, f)



def test_cirkl(table):
   # table=table["asset"].apply(func_2)
    table_a = table.copy()
    table_convert=table_a.to_json(orient="index")
    write_json(table_convert)
    while True:
        time.sleep(1)
        table = fun_1(table)
        table_a=table.copy()


def grapf(a):
    fig = go.Figure(data=[go.Candlestick(x=a.day_set.index,
                    open=a.day_set['Open'],
                    high=a.day_set['High'],
                    low=a.day_set['Low'],
                    close=a.day_set['Close'])])
    fig.show()

table=fun_1(table)#Вызов базовой таблицы

if __name__ == '__main__':
    test_cirkl(table)


