# Сортино
import binance2 as bs
import datetime
import pandas as pd
import math
import xlwings as xw
import datetime

client=bs.client
def fun_atr(table_data):
    '''Скользящее среднее'''
    Candle_close = table_data["Close"]
    Candle_hight = table_data["High"]
    Candle_low = table_data["Low"]
    table_data["raznost1"] = Candle_hight - Candle_low

    table_data["raznost2"] = abs(Candle_hight - Candle_close.shift(-1))
    table_data["raznost3"] = abs(Candle_low - Candle_close.shift(-1))
    table_data['atr'] = table_data[["raznost1", "raznost2", "raznost2"]].max(axis=1)
    table_data=table_data.dropna(axis=0)
    print (table_data)
    atr = table_data["atr"].sum() / len(table_data)


    return atr





def fun_sharp_(table_data):
    atr = fun_atr(table_data)  # Нахождение скользящего среднего

    standart_dohodn = 0
    number_of_day = len(table_data)

    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность шарп"] = Candle_close.diff() / Candle_close.shift(-1)
    srednee_znac_dohodn = table_data["Доходность шарп"].mean()
    Rf = standart_dohodn / 365  # доходность дневная без рисковая
    standart_dev = table_data["Доходность шарп"].std()  # Стандартное отклонение
    #sharp = (srednee_znac_dohodn - Rf) / standart_dev * (52 ** (1 / 2))  # Через стандартное отклонение
    sharp = (srednee_znac_dohodn - Rf) /(standart_dev) ** (1 / 2)  # Через стандартное отклонение
    #sharp = (srednee_znac_dohodn - Rf) / atr**(1/2)

    # print(table_data)
    # print(f"коэффициент Шарпа {sharp}")
    return (sharp)


def fun_sortino_(table_data):
    standart_dohodn = 4
    number_of_day = len(table_data)
    # table_data = table_data[(table_data['Close']) > 0]# Сомнительная строка !!!!! Так как доходность и так всегда больше нуля
    Rf = standart_dohodn / 365  # доходность дневная без рисковая

    Candle_close = table_data["Close"]
    # iat
    table_data["Доходность сортино"] = Candle_close.diff() / Candle_close.shift(-1)  # Нахождение разницы в процентах
    srednee_znac_dohodn = table_data["Доходность сортино"].mean()

    standart_dev = table_data["Доходность сортино"].std()  # Стандартное отклонение

    difference = (Rf - table_data[
        "Доходность сортино"]) ** 2  # Для знаменателя разность стандартной доходности и реальной возведенна в квадра

    # print(table_data)
    profitability = difference.mean()  # Среднеее значение по разности доходности для знаменателя
    sortino = (srednee_znac_dohodn - Rf) / profitability ** (1 / 2)
    return sortino


class Candle_class:
    def __init__(self, table_data):

        self.candle_open = table_data["Open"]
        self.candle_hight = table_data["High"]
        self.candle_low = table_data["Low"]
        self.candle_close = table_data["Close"]
        self.atr=fun_atr(table_data)
        self.candle_model["свеча"] = table_data

    def candel_classificator(self):
        '''Определяет тип свечей'''
        pogreshost = 0.5
        candel_scope = self.candle_low - self.candle_hight  # Размах свечи
        candel_size = math.fabs(self.candle_open - self.candle_close)  # Тело свечи
        candel_relation = candel_size / self.candle_close  # Отношение цены открытия к цене закрытия
        bottomShadow = min(self.candle_open, self.candle_close) - self.candle_low  # Нижняя тень  размер
        topShadow = self.candle_hight - max(self.candle_open, self.candle_close)  # Верхняя тень

        if bottomShadow > candel_size * 2 and topShadow < 0.1 * candel_scope:
            self.candle_type = "Молот"
        elif topShadow > candel_size * 2 and bottomShadow < 0.1 * candel_scope:
            self.candle_type = "Такури"  # Зонтик висильник
        elif candel_size < 0.1 * candel_scope and candel_relation < 0.005:  # вопросик по поводу диапазона
            self.candle_type = "Додзи"
        elif bottomShadow < topShadow * 4 and candel_relation < 0.005:
            self.candle_type = "стрекоза"
        elif (candel_scope - candel_size) / candel_scope < 0.02:
            self.candle_type = "Белый больш свеча"
        return self.candle_type


def take_data_candle(asset, daily_interval):
    '''
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
]'''
    # symbol=table.asset[1] # Выбор символа
    # print (symbol)
    interval = '1d'
    # start_str=datetime.datetime(2021,1,1)
    time_delta = datetime.timedelta(daily_interval)  # Интервал вычесления в днях
    time_delta = time_delta.total_seconds()
    print(bs.current_time, time_delta)
    start_str = bs.current_time['serverTime'] / 1000 - time_delta

    # start_str=str(time.mktime(start_str.timetuple()))
    print("time", str(start_str))
    print(f"инструмент {asset}")
    try:
        data = bs.client.get_historical_klines(asset + "USDT", interval, str(start_str), end_str=None, limit=500)
    except:
        return pd.DataFrame([[None, None, None, None]], columns=["Open", "Close", "High", "Low"])

    table_data = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                                             "Close time", "Quote asset volume", "Number of trades",
                                             "Taker buy base asset volume",
                                             "Taker buy quote asset volume", "Can be ignored"])

    table_data = table_data[["Open", "Close", "High", "Low"]].applymap(lambda x: float(x))
    print(table_data)
    return table_data


def find_sharp_sortino(asset, daily_interval):
    '''Функция запуска Шарпа и Сортино и объединения функций'''

    table_data = take_data_candle(asset, daily_interval)
    print(table_data)
    sharpa = fun_sharp_(table_data)
    sortino = fun_sortino_(table_data)  # Запуск функции пересчета Шарпа
    # atr = fun_atr(table_data)# Значение скольязящего среднего может потом пригодится
    print(f"Коэффициент {sharpa},Коэффициент Сортино 0{sortino}")
    return pd.Series([sharpa, sortino])


def candel_classificator(table_data, daily_interval):
    '''Определяет тип свечей'''
    table_data = take_data_candle(table_data, daily_interval)  # Запускаем поиск свечей в интервале.
    table_data = take_data_candle(table_data, daily_interval)
    candle_open = table_data["Open"]
    candle_hight = table_data["High"]
    candle_low = table_data["Low"]
    candle_close = table_data["Close"]

    pogreshost = 0.5
    candel_scope = candle_low - candle_hight  # Размах свечи
    candel_size = math.fabs(candle_open - candle_close)  # Тело свечи
    candel_relation = candel_size / candle_close  # Отношение цены открытия к цене закрытия
    bottomShadow = min(candle_open, candle_close) - candle_low  # Нижняя тень  размер
    topShadow = candle_hight - max(candle_open, candle_close)  # Верхняя тень

    if bottomShadow > candel_size * 2 and topShadow < 0.1 * candel_scope:
        candle_type = "Молот"
    elif topShadow > candel_size * 2 and bottomShadow < 0.1 * candel_scope:
        candle_type = "Такури"  # Зонтик висильник
    elif candel_size < 0.1 * candel_scope and candel_relation < 0.005:  # вопросик по поводу диапазона
        candle_type = "Додзи"
    elif bottomShadow < topShadow * 4 and candel_relation < 0.005:
        candle_type = "стрекоза"
    elif (candel_scope - candel_size) / candel_scope < 0.02:
        candle_type = "Белый больш свеча"
    return candle_type


def ask_input():
    'Функция ввода данных'
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
    '''Функция для вставки в excel'''
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
    # bs.table_base=bs.table_base.loc[1:4]
    # test(bs.table_base)
    # bs.table_base = bs.table  # Если надо найти по портфелю Шарпа включить эту строку.
    # print( bs.table)
    # take_data_candle(bs.table_base)

    bs.table_base[["Sharp_14", "Sortino_14"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 14))  # Инициализация функции поиска
    bs.table_base[["Sharp_60", "Sortino_60"]] = bs.table_base["asset"].apply(
        lambda x: find_sharp_sortino(x, 60))  # Инициализация функции поиска

    column_name = ["asset", "Sharp_14", "Sortino_14", "Sharp_60", "Sortino_60"]
    bs.table_base = bs.table_base.dropna(subset=["Sortino_14"])
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
