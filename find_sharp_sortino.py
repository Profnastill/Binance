# Сортино
import binance2 as bs
import datetime
import pandas as pd


def fun_sharp_(table_data):
    standart_dohodn = 0
    number_of_day = len(table_data)
    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность шарп"] = Candle_close.diff() / Candle_close.shift(-1)
    srednee_znac_dohodn = table_data["Доходность шарп"].mean()
    Rf = standart_dohodn / 365  # доходность дневная без рисковая
    standart_dev = table_data["Доходность шарп"].std()  # Стандартное отклонение

    sharp = (srednee_znac_dohodn - Rf) / standart_dev * (52 ** 1 / 2)  # Через стандартное отклонение
    #print(table_data)
    #print(f"коэффициент Шарпа {sharp}")
    return (sharp)


def fun_sortino_(table_data):
    standart_dohodn = 4
    number_of_day = len(table_data)
    table_data = table_data[(table_data['Close']) > 0]
    Rf = standart_dohodn / 365  # доходность дневная без рисковая

    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность сортино"] = Candle_close.diff() / Candle_close.shift(-1)
    srednee_znac_dohodn = table_data["Доходность сортино"].mean()

    standart_dev = table_data["Доходность сортино"].std()  # Стандартное отклонение

    difference = (Rf - table_data[
        "Доходность сортино"]) ** 2  # Для знаменателя разность стандартной доходности и реальной возведенна в квадра

    #print(table_data)
    profitability = difference.mean()  # Среднеее значение по разности доходности для знаменателя
    sortino = (srednee_znac_dohodn - Rf) / profitability ** 1 / 2
    return sortino


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
    # print (symbol)
    interval = '1d'
    # start_str=datetime.datetime(2021,1,1)
    time_delta = datetime.timedelta(10)  # Интервал вычесления в днях
    time_delta = time_delta.total_seconds()
    print(bs.current_time, time_delta)
    start_str = bs.current_time['serverTime'] / 1000 - time_delta

    # start_str=str(time.mktime(start_str.timetuple()))
    print("time", str(start_str))
    print(f"инструмент {asset}")
    try:
        data = bs.client.get_historical_klines(asset + "USDT", interval, str(start_str), end_str=None, limit=500)
    except:
        data = None
    print(data)
    if data != None:
        table_data = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                                                 "Close time", "Quote asset volume", "Number of trades",
                                                 "Taker buy base asset volume",
                                                 "Taker buy quote asset volume", "Can be ignored"])
        print(table_data)
        print(table_data, int(len(table_data)))
        table_data["Close"] = table_data["Close"].apply(lambda x: float(x))



        print("Шарп")
        sharpa = fun_sharp_(table_data)
        print("Сортино")
        sortino = fun_sortino_(table_data)  # Запуск функции пересчета Шарпа


        print (table_data)
        print(f"Коэффициент {sharpa},Коэффициент Сортино {sortino}")
        return pd.Series([sharpa,sortino])
    else:
        return pd.Series([None,None])


if __name__ == '__main__':
    bs.table_base=bs.table_base[7:10]
    #bs.table_base = bs.table  # Если надо найти по портфелю Шарпа включить эту строку.
    # print( bs.table)
    take_data_candle(bs.table_base)

    bs.table_base[["Sharp","Sortino"]] = bs.table_base["asset"].apply(
        lambda x: take_data_candle(x))  # Инициализация функции поиска
    # bs.table_base["Sortino"] = bs.table_base["asset"].apply(lambda x: take_data_candle(x))  # Инициализация функции поиска

    bs.table_base = bs.table_base.dropna(subset=["Sortino"])
    print("-" * 10)
    print(bs.table_base)

    bs.table_base.sort_values(by="Sortino", inplace=True)
    bs.table_base.drop(["free","locked"],axis='columns', inplace=True)
    bs.table_base.reset_index(drop=True,inplace=True)
    # print(bs.table_base)
    bs.table_base = bs.table_base[-20::1]
    print("-" * 20)
    print(bs.table_base)
