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


table=table[(table['free'])>0]
table.sort_values(by=['free'],axis=0,inplace=True,ascending=False) #Сортировка
table=table.set_index(table.columns[0])
table=table.reset_index("asset")

selection_usdt = table.asset == "USDT"
volume_usdt=float(table[selection_usdt]["free"])
table = table[~selection_usdt]# Очистка таблицы от доллара


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


def sharp_table_updater(table_data):
    standart_dohodn=0
    number_of_day=len(table_data)

    Candle_close=table_data["Close"]
    #iat
    table_data["Доходность"]=Candle_close.diff()/Candle_close.shift(-1)
    srednee_znac_dohodn=table_data["Доходность"].mean()
    Rf=standart_dohodn/365*number_of_day# доходность дневная без рисковая
    standart_dev=table_data["Доходность"].std()# Стандартное отклонение

    sharp= (srednee_znac_dohodn - Rf)/standart_dev*(52**1/2) # Через стандартное отклонение
    print (table_data)
    print (f"коэффициент Шарпа {sharp}")
    return (sharp)


def take_data_candle(asset):

    '''[
    [
        1499040000000,      # Open time
        "0.01634790",       # Open
        "0.80000000",       # High
        "0.01575800",       # Low
        "0.01577100",       # Close
        "148976.11427815",  # Volume
        1499644799999,      # Close time
        "2434.19055334",    # Quote asset volume
        308,                # Number of trades
        "1756.87402397",    # Taker buy base asset volume
        "28.46694368",      # Taker buy quote asset volume
        "17928899.62484339" # Can be ignored
    ]
]'''
   # symbol=table.asset[1] # Выбор символа
    #print (symbol)
    interval='1d'
    #start_str=datetime.datetime(2021,1,1)
    time_delta=datetime.timedelta(30)
    time_delta=time_delta.total_seconds()
    print(current_time,time_delta)
    start_str=current_time['serverTime']/1000-time_delta

    #start_str=str(time.mktime(start_str.timetuple()))
    print("time",str(start_str))

    data=client.get_historical_klines(asset+"USDT", interval, str(start_str), end_str=None, limit=500)
    table_data=pd.DataFrame(data,columns=["Open time","Open","High","Low","Close","Volume",
                                          "Close time","Quote asset volume","Number of trades",
                                          "Taker buy base asset volume",
                                          "Taker buy quote asset volume","Can be ignored"])
    print (table_data,int(len(table_data)))
    table_data["Close"]=table_data["Close"].apply(lambda x:float(x))
    print(table_data)

    sharp=sharp_table_updater(table_data)# Запуск функции пересчета Шарпа
    return sharp




def koeff_sharp(x):
    #S=E*(doxod_R(x))-R_f)/fun_G(x)
    S=(avgR(x)-avgRf)/fun_G(x)
    return S



''''''''''
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
   # take_data_candle(table)
    table["Sharp"]=table["asset"].apply(lambda x: take_data_candle(x))
    print(table)
    funct_1()
   # test_cirkl()

    #print ("Результат ",result)

    def balanse_filter():
        None
    #instrument_list=list(table["asset"])
    #trades = client.get_my_trades(symbol="CTSIUSDT",limit=1)
    candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_30MINUTE)
    print(candles)
    trades = client.get_avg_price(symbol="CTSIUSDT")
    print (trades)