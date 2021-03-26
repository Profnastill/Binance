# Сортино
import binance2 as bs
import datetime
import pandas as pd
import math
import xlwings as xw
import datetime
import numpy as np
import Test_otbor_candle as candlmodelSort

client = bs.client


def fun_atr(table_data):
    """Скользящее среднее
    Принимает таблицу"""
    Candle_close = table_data["Close"]
    Candle_hight = table_data["High"]
    Candle_low = table_data["Low"]
    table_data["raznost1"] = Candle_hight - Candle_low

    table_data["raznost2"] = abs(Candle_hight - Candle_close.shift(-1))
    table_data["raznost3"] = abs(Candle_low - Candle_close.shift(-1))
    table_data['atr'] = table_data[["raznost1", "raznost2", "raznost2"]].max(axis=1)
    table_data = table_data.dropna(axis=0)
    print(table_data)
    atr = table_data["atr"].sum() / len(table_data)
    return atr


def fun_sharp_(table_data):
    """Нахождение значения коэф шарпа пока без atr"""
    # atr = fun_atr(table_data)  # Нахождение скользящего среднего

    standart_dohodn = 0
    # umber_of_day = len(table_data)
    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность шарп"] = Candle_close.diff() / Candle_close.shift(-1)
    srednee_znac_dohodn = table_data["Доходность шарп"].mean()
    Rf = standart_dohodn / 365  # доходность дневная без рисковая
    standart_dev = table_data["Доходность шарп"].std()  # Стандартное отклонение
    # sharp = (srednee_znac_dohodn - Rf) / standart_dev * (52 ** (1 / 2))  # Через стандартное отклонение
    sharp = (srednee_znac_dohodn - Rf) / standart_dev ** (1 / 2)  # Через стандартное отклонение
    # sharp = (srednee_znac_dohodn - Rf) / atr**(1/2)

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

    table_data = table_data[["Open time", "Open", "Close", "High", "Low"]].applymap(lambda x: float(x))
    table_data["Open time"] = table_data["Open time"].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x) / 1000).date())

    print(table_data)
    return table_data


def find_sharp_sortino(asset, daily_interval):
    """Функция запуска Шарпа и Сортино и объединения функций"""
    table_data = take_data_candle(asset, daily_interval)
    print(table_data)
    sharpa = fun_sharp_(table_data)
    sortino = fun_sortino_(table_data)  # Запуск функции пересчета Шарпа
    # atr = fun_atr(table_data)# Значение скольязящего среднего может потом пригодится
    print(f"Коэффициент {sharpa},Коэффициент Сортино 0{sortino}")
    return pd.Series([sharpa, sortino])


def candle_type_analiz(candle, color):
    """Определение типа свечи
    color= бел. or крас. цвет свечи"""
    #print('-x-x-x-'*10)
    #print(candle)




    if (candle['scope']==0) & (candle['size']==0):
        candle_type= f"доджи 4 цен"
    elif ((candle['size'] / candle['mean'] > 1.3) | (candle['size'] / candle['Close'] > 0.05)) \
            & (candle['scope']  < 1.05*candle['size'] ):  # Уточнить размер теней.
        candle_type = f"Больш. {color} свеча"  # Марабудзу
    elif ((candle['size'] / candle['mean'] > 0.3) | (candle['size'] / candle['Close'] > 0.95)) \
            & (candle['scope']   < 1.05*candle['size']):  # Уточнить размер теней.
        candle_type = f"Мален. {color} свеча"
    elif (candle['size'] < 0.5 * candle['bottomShadow']) | (candle['topShadow'] / candle['scope'] < 0.1):
        candle_type = f"{color} зонтик"
    elif (candle['size'] < 0.5 * candle['topShadow']) | (candle['bottomShadow'] / candle['scope'] < 0.1):
        candle_type = f"{color} молот"
    elif 0.01 < candle['size'] / candle['scope'] < 0.03:
        candle_type = f"{color} доджи"
    else:
        candle_type = None
    print('Успешно')
    print(candle_type)
    return candle_type


def candle_color_analiz(candle):
    """Функция обертка  для candle_type_analiz  опеределения типа свечи  по цвету"""
    print(candle)
    print(candle['Open'])
    if candle['Open'] > candle['Close']:  # определяем цвет свечей
        candle['type'] = candle_type_analiz(candle, "бел.")
    else:
        candle['type'] = candle_type_analiz(candle, "крас.")

    return candle['type']


def candle_type_analiz_old(candle):
    """Функйия опеределения типа свечи"""

    if (candle['bottomShadow'] > candle['size'] * 2) & (
            candle['topShadow'] < 0.1 * candle['scope']):  # "Это не работает потому что надо ее к списку применять
        candle['type'] = "Молот"
    elif (candle['topShadow'] > candle['size'] * 2) & (candle['bottomShadow'] < 0.1 * candle['scope']):
        candle['type'] = "Такури"  # Зонтик висильник
    elif (candle['size'] < 0.1 * candle['scope']) & (candle['relation'] < 0.005):  # вопросик по поводу диапазона
        candle['type'] = "Додзи"
    elif (candle['bottomShadow'] < candle['topShadow'] * 4) & (candle['relation'] < 0.005):
        candle['type'] = "стрекоза(Тонбо)"
    elif ((candle['scope'] - candle['size']) / candle['scope']) < 0.02:
        candle['type'] = "Белый больш свеча"
    elif (candle['topShadow'] < 0.1 * candle['scope']) & (candle['scope'] > candle['atr']):
        candle['type'] = "Марубодзу"
    elif (candle['topShadow'] > candle['size'] * 2) & (
            candle['scope'] - candle['topShadow'] - candle['size'] > candle['bottomShadow']):
        candle['type'] = 'Черная свеч с верх тен'

    elif candle['relation'] < 1:
        candle['type'] = None
    else:
        candle['type'] = None
    print("Успешно", candle)
    return candle['type']  #


def candel_classificator(asset, daily_interval):
    """'Определяет параметры свечей для наборов asset использует candle_type_anliz''"""
    print(asset, daily_interval)
    candle = take_data_candle(asset, daily_interval)  # Вытаскиваем значения свечей c промощью функции candle
    pogreshost = 0.5
    print('_' * 10)
    print(candle)

    candle['scope'] = candle['High'] - candle['Low']  # Размах свечи
    candle['size'] = abs(candle['Open'] - candle['Close'])  # Тело свечи

    candle['relation'] = candle['size'] / candle['Close']  # Отношение цены открытия к цене закрытия

    candle['bottomShadow'] = candle[["Open", "Close"]].values.min(1) - candle['Low']  # Нижняя тень  размер
    candle['topShadow'] = candle['High'] - candle[["Open", "Close"]].values.max(1)

    # candle['type']= np.where((candle['bottomShadow'] > candle['size'] * 2) & (candle['topShadow'] < 0.1 *  candle['scope']),"Молот")
    candle['atr'] = (fun_atr(candle))  # Для указанной таблицы расчитываем ATR

    candle['mean'] = candle['size'].mean(axis=0)
    print('-//--' * 10)
    #print(candle)
    # candle['type'] = candle.apply(candle_type_analiz,axis=1)  # Получаем множество свечей для заданного asset для каждого дня
    candle['type'] = candle.apply(candle_color_analiz, axis=1)# Определяем типы свечей для asset
    select_candle = candle['type'][-3::1].tolist()  # Выбрали свечи за последние три дня
    #print(candle)
    #rezult=  (candlmodelSort.candles_model_analiz(candle))# Запуск модуля проверки моделей


    return [[select_candle],"хрен"]


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


if __name__ == '__main__':
    bs.table_base = ask_input()
    print(bs.table_base)
    bs.table_base = bs.table_base.loc[1:2]
    # test(bs.table_base)
    # bs.table_base = bs.table  # Если надо найти по портфелю Шарпа включить эту строку.
    # print( bs.table)
    # take_data_candle(bs.table_base)

    bs.table_base[["Sharp_14", "Sortino_14"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 14))  # Инициализация функции поиска
    bs.table_base[["Sharp_60", "Sortino_60"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 60))  # Инициализация функции поиска

    column_name = ["asset", "Sharp_14", "Sortino_14", "Sharp_60", "Sortino_60"]

    bs.table_base = bs.table_base.dropna(subset=["Sortino_14"])  # Удаляем потеренные значения

    bs.table_base[["Тип свечи","Сигнал_модель"]] = bs.table_base["asset"].apply(
        lambda x: candel_classificator(x, 14))  # Запускаем поисковик свечей

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

    insert_excel(bs.table_base)  # Функция для вставки в текущий excel
    print("-" * 20)
    print(bs.table_base)
