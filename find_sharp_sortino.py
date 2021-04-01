# Сортино
import binance2 as bs
import datetime
import pandas as pd
import math
import xlwings as xw
import datetime
import numpy as np
import Test_otbor_candle as candlmodelSort

pd.options.display.max_rows = 1000
pd.options.display.max_columns = 20
pd.options.display.expand_frame_repr = False

client = bs.client


def fun_atr(table_data):
    """Скользящее среднее
    Принимает таблицу"""
    Candle_close = table_data["Close"]
    Candle_hight = table_data["High"]
    Candle_low = table_data["Low"]
    table_data["raznost1"] = abs(Candle_hight - Candle_low)

    table_data["raznost2"] = abs(Candle_hight - Candle_close.shift(periods=-1))
    table_data["raznost3"] = abs(Candle_low - Candle_close.shift(periods=-1))

    print('разность', Candle_low, abs(Candle_close.shift(periods=-1)))
    table_data['atr'] = table_data[["raznost1", "raznost2", "raznost2"]].max(axis=1)
    print(table_data)
    table_data = table_data.dropna(axis=0)
    # print(table_data)

    atr = table_data["atr"].mean()

    return atr


def fun_sharp_(table_data):
    """Нахождение значения коэф шарпа пока без atr"""
    atr = fun_atr(table_data)  # Нахождение скользящего среднего

    standart_dohodn = 0
    # umber_of_day = len(table_data)
    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность шарп"] = Candle_close.diff() / Candle_close.shift(-1)
    srednee_znac_dohodn = table_data["Доходность шарп"].mean()
    Rf = standart_dohodn / 365  # доходность дневная без рисковая
    standart_dev = table_data["Доходность шарп"].std(skipna=True)  # Стандартное отклонение
    # sharp = (srednee_znac_dohodn - Rf) / standart_dev * (52 ** (1 / 2))  # Через стандартное отклонение
    sharp = (srednee_znac_dohodn - Rf) / standart_dev  # Через стандартное отклонение
    # sharp = (srednee_znac_dohodn - Rf) / atr
    print(f'стандарное откл= {standart_dev}, atr={atr}')

    # print(table_data)
    # print(f"коэффициент Шарпа {sharp}")
    return sharp


def fun_sortino_(table_data):
    standart_dohodn = 4
    # number_of_day = len(table_data)
    # table_data = table_data[(table_data['Close']) > 0]# Сомнительная строка !!!!! Так как доходность и так всегда больше нуля
    Rf = standart_dohodn / 365  # доходность дневная без рисковая

    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность сортино"] = Candle_close.diff() / Candle_close.shift(-1)  # Нахождение разницы в процентах
    srednee_znac_dohodn = table_data["Доходность сортино"].mean()

    # standart_dev = table_data["Доходность сортино"].std()  # Стандартное отклонение

    difference = (Rf - table_data[
        "Доходность сортино"]) ** 2  # Для знаменателя разность стандартной доходности и реальной возведенна в квадра

    # print(table_data)
    profitability = difference.mean()  # Среднеее значение по разности доходности для знаменателя
    sortino = (srednee_znac_dohodn - Rf) / profitability ** (1 / 2)
    return sortino


def take_data_candle(asset, daily_interval):
    """
 Функция обработки таблицы для извленения по интервалу и времени параметров свечей.
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
]"""

    interval = '1d'
    time_delta = datetime.timedelta(daily_interval + 1)  # Интервал вычесления в днях
    time_delta = time_delta.total_seconds()
    print(bs.current_time, time_delta)
    start_str = bs.current_time['serverTime'] / 1000 - time_delta

    end_day = bs.current_time['serverTime'] / 1000 - (datetime.timedelta(1)).total_seconds()  # Окончания поиска.

    print("time", str(start_str))
    print(f"инструмент {asset}")
    try:
        data = bs.client.get_historical_klines(asset + "USDT", interval, str(start_str), end_str=str(end_day),
                                               limit=500)
    except:
        return pd.DataFrame([[None, None, None, None]], columns=["Open", "Close", "High", "Low"])

    table_data = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                                             "Close time", "Quote asset volume", "Number of trades",
                                             "Taker buy base asset volume",
                                             "Taker buy quote asset volume", "Can be ignored"])

    table_data = table_data[["Open time", "Open", "Close", "High", "Low", "Volume"]].applymap(lambda x: float(x))
    table_data["Open time"] = table_data["Open time"].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x) / 1000).date())

    print(table_data)
    return table_data


def find_sharp_sortino(asset, daily_interval):
    """Функция запуска Шарпа и Сортино и объединения функций"""
    table_data = take_data_candle(asset, daily_interval)
    sharpa = fun_sharp_(table_data)
    sortino = fun_sortino_(table_data)  # Запуск функции пересчета Шарпа
    # atr = fun_atr(table_data)# Значение скольязящего среднего может потом пригодится
    print(f"Коэффициент {sharpa},Коэффициент Сортино 0{sortino}")
    return pd.Series([sharpa, sortino])


def candle_type_analiz(candle):
    """Определение типа свечи
    Принимаете таблицу свечей  для asset
    color= бел. or крас. цвет свечи"""
    if candle['Open'] < candle['Close']:  # определяем цвет свечей
        color = "бел."
    else:
        color = "крас."
    koef = 1.5  # Коэффициент для отладки моделей процентное отношение
    koef_2 = 0.15

    if (candle['scope'] == 0) & (candle['size'] == 0):
        candle_type = f"доджи 4 цен"
    elif ((candle['size'] / candle['candl_mean'] > 1.3)) \
            & (candle['scope'] < koef * candle['size']):  # Уточнить размер теней.
        candle_type = f"Больш. {color} свеча"  # Марабудзу | (candle['size'] / candle['Open'] > 0.05)

    elif ((candle['size'] / candle['candl_mean'] > 0.3)) \
            & (candle['scope'] < 1.05 * candle[
        'size']):  # Уточнить размер теней. | (candle['size'] / candle['Open'] > 0.95)
        candle_type = f"Мален. {color} свеча"
    elif (candle['size'] < 0.5 * candle['bottomShadow']) & (candle['topShadow'] / candle['scope'] < 0.1):
        candle_type = f"{color} зонтик"
    elif (candle['size'] < 0.5 * candle['topShadow']) & (candle['bottomShadow'] / candle['scope'] < 0.1):
        candle_type = f"{color} молот"
    elif 0.01 < candle['size'] / candle['scope'] < 0.03:
        candle_type = f"{color} доджи"
    else:
        candle_type = None
    return candle_type


def fun_volume(data):
    '''Функция вычесления объем принимает свечу дневную'''
    #data['изм Объема %'] = (data['Volume'] / data['volume_mean'] - 1) * 100
    data['изм Объема %'] = (data['Volume'] / data['volume_mean'])# Черех стандартное отклонение
    return data['изм Объема %']


def candel_classificator(asset, daily_interval):
    """'Определяет параметры свечей для наборов asset использует candle_type_anliz''"""
    candle = take_data_candle(asset, daily_interval)  # Вытаскиваем значения свечей c промощью функции candle
    pogreshost = 0.5
    candle['scope'] = candle['High'] - candle['Low']  # Размах свечи
    candle['size'] = abs(candle['Open'] - candle['Close'])  # Тело свечи
    candle['relation'] = candle['size'] / candle['Close']  # Отношение цены открытия к цене закрытия
    candle['bottomShadow'] = candle[["Open", "Close"]].values.min(1) - candle['Low']  # Нижняя тень  размер
    candle['topShadow'] = candle['High'] - candle[["Open", "Close"]].values.max(1)
    candle['atr'] = (fun_atr(candle))  # Для указанной таблицы расчитываем ATR
    candle['candl_mean'] = candle['size'].std(axis=0)

    # print(asset, daily_interval)
    # print(candle)
    candle['volume_mean'] = candle['Volume'].mean(axis=0)# Раассчитываем для полного выбора 10 дней

    select_candle = candle[-3::1]  # Выбрали свечи за последние три дня

    time = (select_candle['Open time'][0:1:1].values)
    select_candle['type'] = select_candle.apply(candle_type_analiz, axis=1)  # Определяем типы свечей для asset

    select_candle['изм Объема %'] = select_candle.apply(fun_volume, axis=1)  # Запуск функции изменения объема
    candle_volume_max = select_candle['изм Объема %'].max()

    model_rezult = (candlmodelSort.candles_model_analiz(select_candle))  # Запуск модуля проверки моделей

    return pd.Series([time[0], str(list(select_candle['type'])), str(model_rezult), candle_volume_max])


def ask_input():
    """Функция ввода данных"""
    try:
        a = int(input("Введите по какой таблице искать по портфелю 1 или по рынку 0 "))
    except:
        "Ввели не числовые данные"
        ask_input()
    if a == 1:
        bs.table_base = bs.table
        return bs.table_base
    else:
        bs.table_base = bs.table_base

        return bs.table_base


def insert_excel(table):
    """Функция для вставки в excel"""
    a = int(input("Введите нужен ли импорт в excel Yes=1 "))
    if a == 1:
        date = str(datetime.date.today())
        xlbook = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
        try:
            xlsheet = xlbook.sheets.add(name=date)
        except:
            xlsheet = xlbook.sheets(date)

        xlsheet.range("A1").options(index=False).value = table


def convert(time):
    return pd.Timestamp(time.timestamp(), unit='s')


if __name__ == '__main__':
    bs.table_base = ask_input()
    print(bs.table_base)
    #bs.table_base = bs.table_base.loc[1:2]


    bs.table_base[["Sharp_14", "Sortino_14"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 14))  # Инициализация функции поиска
    bs.table_base[["Sharp_60", "Sortino_60"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 60))  # Инициализация функции поиска

    column_name = ["asset", "Sharp_14", "Sortino_14", "Sharp_60", "Sortino_60"]

    bs.table_base = bs.table_base.dropna(subset=["Sortino_14"])  # Удаляем потеренные значения

    bs.table_base[["Время", "Тип свечи", "Сигнал_модель", "изм Объема"]] = bs.table_base["asset"].apply(
        lambda x: candel_classificator(x, 10))  # Запускаем поисковик свечей

    print("-" * 10)
    print(bs.table_base)

    bs.table_base.sort_values(by=["Sortino_14", "Sharp_14"], inplace=True)

    bs.table_base.drop(["free", "locked"], axis='columns', inplace=True)
    bs.table_base.reset_index(drop=True, inplace=True)
    # print(bs.table_base)
    max_ = ["max"] + (
        list(bs.table_base[column_name[1:]].max()))  # Значения для определения дипазаона возможных значений
    print(max_)
    min_ = ["min"] + (list(bs.table_base[column_name[1:]].min()))
    max_min = [dict(zip(column_name, max_)), dict(zip(column_name, min_))]
    print(max_min)

    bs.table_base = bs.table_base[-22::1]  # Таблица с шарпом

    # bs.table_base=pd.concat([bs.table_base,max_,min_],axis=1,)

    bs.table_base = bs.table_base.append(max_min, ignore_index=True, sort=False)
    print(bs.table_base)

    insert_excel(bs.table_base)  # Функция для вставки в текущий excel
    print("-" * 20)
    print(bs.table_base)
