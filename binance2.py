import binance
import pandas as pd
from binance.client import Client
import urllib3
import json
import time
pd.options.display.max_rows=1000
pd.options.display.max_columns=10
pd.options.display.expand_frame_repr = False
urllib3.disable_warnings()




#API_key = "New_key"
API_key = "TNrtfAy5UIWUK2eqg1KupoF5JFErh7XVJBSONM3PrLbCtiz3XVZ0379e1HDwdJyG"
API_Secret = "SEPEd0ME1qUsbOp69YQ5ze6o5c0hYRQQvfjFO3ShtO0THhK14FKVVuPINqmNxpWn"

converter = lambda x : x*2 if x < 11 else (x*3 if x < 22 else x)


client = Client(API_key, API_Secret)
current_time=client.get_server_time()
print(current_time)
print (client)
client = Client(API_key, API_Secret, {"verify": False, "timeout": 20})
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
table=table[(table['free'])>0]
table.sort_values(by=['free'],axis=0,inplace=True,ascending=False) #Сортировка
table=table.set_index(table.columns[0])
table=table.reset_index("asset")

table["free"]=table["free"].apply(lambda x: float(x))
selection_usdt = table.asset == "USDT"

volume_usdt=float(table[selection_usdt]["free"])

table = table[~selection_usdt]
def write_json(data):
    with open(r'C:\Users\Давид\PycharmProjects\Binance\data.json', 'w') as f:json.dump(data, f)


def funct_1():

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
        print(table)
        stoimost={"Стоимост активов $":sum_cost + volume_usdt}
        print(f"Стоимость активов в долларах={sum_cost + volume_usdt}\n"
              f"Стоимость активов в рублях {(sum_cost + volume_usdt) * usd_rub}\n"
              f"Наличные доллары$ {volume_usdt}")



table=funct_1()
test_cirkl()

#print ("Результат ",result)






def balanse_filter():
    None
#instrument_list=list(table["asset"])
#trades = client.get_my_trades(symbol="CTSIUSDT",limit=1)
candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_30MINUTE)
print(candles)
trades = client.get_avg_price(symbol="CTSIUSDT")
print (trades)