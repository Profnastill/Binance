# Программа находит коэффцииент шарпа и сортино одновременно



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
API_key = "xY9wlXlxoP27hZHUN7KAqYpLzDXvCmYmNKs4AGwehHFUAI1Jz4yrWRQxWiC9Gzp8"
API_Secret = "6ZEuiRDt1HTkXsA36JF2D6EmFzzoKglmg6zWbsf7cuGSjaiBdtE1PNav5XS8RlLq"

converter = lambda x : x*2 if x < 11 else (x*3 if x < 22 else x)


client = Client(API_key, API_Secret)
current_time=client.get_server_time()
print(current_time['serverTime'])

time_dd_format=time.ctime(current_time['serverTime']/1000)
print(time_dd_format)




print (client)
#client = Client(API_key, API_Secret, {"verify": False, "timeout": 20})

info = client.get_account()
print (info)
usd_rub=float(client.get_avg_price(symbol="USDTRUB")["price"])
print (usd_rub)

status = client.get_account_status()
print (status)
#balance = client.get_deposit_history

balance=client.get_account()['balances']
print(balance)
table=pd.DataFrame(balance)
table['free']=table['free'].apply(lambda x: float(x))
table_base=table.copy(deep=True)

table = table[(table['free']) > 0]
table.sort_values(by=['free'], axis=0, inplace=True, ascending=False)  # Сортировка
table = table.set_index(table.columns[0])
table = table.reset_index("asset")
selection_usdt = table.asset == "USDT"
volume_usdt = float(table[selection_usdt]["free"])
table = table[~selection_usdt]  # Очистка таблицы от доллара

print("11")


def write_json(data):
    with open(r'C:\Users\Давид\PycharmProjects\Binance\data.json', 'w') as f:json.dump(data, f)


def funct_1():
    """"Отделяем доллары от основной таблицы"""


    table["Price_USDT"] = table["asset"].apply(lambda x:    float(client.get_avg_price(symbol=x + "USDT")["price"]))  # Получаем цену текущую активов.
    table['USDT_cost'] = table["free"] * table["Price_USDT"] # Стоимость активов в долларах
    table['RUB_cost']=table['USDT_cost']*usd_rub
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
        print(f"Стоимость активов в долларах={sum_cost + volume_usdt}\n"
              f"Стоимость активов в рублях {(sum_cost + volume_usdt) * usd_rub}\n"
              f"Наличные доллары$ {volume_usdt}")



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


if __name__ == '__main__':
    funct_1()
    test_cirkl()

