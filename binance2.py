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


pd.options.display.max_rows=1000
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
table_base=table.copy(deep=True)


table = table.set_index(table.columns[0])
  # Очистка таблицы от доллара
table = table.reset_index("asset")

selection_usdt = (table.asset == "USDT") | (table.asset ==  'SPARTA')

volume_usdt = table[selection_usdt]['free'].apply(lambda x: float(x))


print(volume_usdt)
table = table[~selection_usdt]

table = table[(table['free']) > 0]

table.sort_values(by=['free'], axis=0, inplace=True, ascending=False)  # Сортировка

table = table.reset_index(drop=True)


def write_json(data):
    with open(r'C:\Users\Давид\PycharmProjects\Binance\data.json', 'w') as f:json.dump(data, f)


def func_2(asset):
    x=asset
    try:
        val=float(client.get_avg_price(symbol=x + 'USDT')["price"])
    except:
        val=float(client.get_avg_price(symbol=x + 'BNB')["price"])
    return val
    # приписать что если не смогла ничего найти



def funct_1(tiker='USDT'):
    """"Отделяем доллары от основной таблицы"""
    tiker='USDT'# USDT
    table["Price_USDT"] = table["asset"].apply(lambda x: float(client.get_avg_price(symbol=x + tiker)["price"]))  # Получаем цену текущую активов.
    table['USDT_cost'] = table["free"] * table["Price_USDT"] # Стоимость активов в долларах
    table['RUB_cost']=table['USDT_cost']*usd_rub#usd_rub
    return table

def test_cirkl():
    table=funct_1()

    table_a = table.copy()
    table_convert=table_a.to_json(orient="index")
    write_json(table_convert)

    while True:
        time.sleep(1)
        table = funct_1()
        table["%"]=(table_a["Price_USDT"]/table["Price_USDT"]-1)*100
        table_a=table.copy()
        resul_plot()


def resul_plot():
        sum_cost = table['USDT_cost'].sum()
        table["percent_balance"] = table["USDT_cost"] / (sum_cost + volume_usdt) * 100  # Таблица с данными
        cols = table.pop('percent_balance')
        table.insert(1,'percent_balance',cols,allow_duplicates=True)

        print(table)
        stoimost={"Стоимост активов $":sum_cost + volume_usdt}
        print("\n"*2)
        print(f"Стоимость активов в долларах={sum_cost + volume_usdt}\n"
              f"Стоимость активов в рублях {(sum_cost + volume_usdt) * usd_rub}\n"
              f"Наличные доллары$ {volume_usdt}")
        print("\n"*2)
        return table


'''''''''
    for i in range (0,len(table_data["Open time"])-1):
        table_data["Доходность"]=table_data[i]
'''''''''


def grapf(a):
    fig = go.Figure(data=[go.Candlestick(x=a.day_set.index,
                    open=a.day_set['Open'],
                    high=a.day_set['High'],
                    low=a.day_set['Low'],
                    close=a.day_set['Close'])])
    fig.show()

table=funct_1()
table=resul_plot()# Таблица с перечнем текущих инструментов в портфеле


if __name__ == '__main__':
    test_cirkl()


