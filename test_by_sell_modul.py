"""Модуль тестировки торговой стратегии с подбором весов к графикам"""

import datetime
from datetime import date
from itertools import *

import pandas as pd
from numpy import arange
from find_sharp_sortino import insert_excel
from candle_graf_class import graf_delta_cls

# import balance_mod

pd.options.display.max_rows = 100
pd.options.display.max_columns = 100
pd.options.display.expand_frame_repr = False


def read_csv_test_():
    """читаем базу с данными возвращаем сигнал"""
    tcur_time = date.today()
    tcur_time = tcur_time.strftime("%m%d%Y")
    print("время", tcur_time)
    # table=table['asset']
    name = "all_find_signal"

    last_signal_table = pd.read_csv(f'B:/download/test_base_BTC.csv')

    last_signal_table = last_signal_table.iloc[:, 1:18]
    last_signal_table = last_signal_table.rename({"Open time.1": "Open time"}, axis=1)
    last_signal_table['Open time'] = last_signal_table['Open time'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
    last_signal_table = last_signal_table.set_index(["Open time"])
    print(last_signal_table)
    # last_signal_table.reset_index(inplace=True, drop=True)
    last_signal_table['asset'] = last_signal_table['asset'].apply(lambda x: x.replace('/USD', ''))
    return last_signal_table


class portf_cls:
    """Класс портфель"""

    def __init__(self, balance):
        self.__balance = balance
        self.__free = 0
        self.price = 0
        self.__comissia = 0.1

    def __set_free(self, count):
        print(f"Цена {self.price}")
        # print("2---", count * self.price + (count * self.price * self.__comissia), self.__balance, self.__free, count)
        if count * self.price + (count * self.price * self.__comissia) <= self.__balance and self.__free + count >= 0:
            self.__free += count
            self.__balance -= count * self.price + count * self.price * self.__comissia
            print(f"Куплено {count}")

    def __get_balance(self):
        print(f"Баланс текущий {self.__balance}")
        return self.__balance

    def __get_free(self):
        print(f"количество текущее {self.__free}")
        return self.__free

    def __get_cost(self):
        """Стоимость всего портфеля"""
        cost = self.__balance + self.price * self.__free
        return cost

    free = property(__get_free, __set_free)
    balance = property(__get_balance)
    port_cost = property(__get_cost)


class balance():
    """
    Функция рассчета покупки продажи в зависимости от сигнала.
    """

    def __init__(self, data_table: pd.DataFrame, porog):
        self.portf = portf_cls(10000)  # Инициализируем класс портфеля
        self.start_traiding_date = datetime.date(2021, 6, 10)  # Время начала торговли
        self.data_tb = data_table.copy(deep=True)
        self.free = 0
        self.comissia = 0.03  # Комиссия в процентах
        self.porog_by = porog  # Пороговое значение для покупки и продажи
        self.standart_dohodn = 4.5
        self._dey_changer()

    def fun_sortino_(self, table_data: pd.DataFrame):


        Rf = self.standart_dohodn / 365  # доходность дневная без рисковая
        Candle_close = table_data["Close"]

        table_data["%Отношение"] = ( Candle_close / Candle_close.shift(1)-1)*100  # Нахождение разницы в процентах


        srednee_znac_dohodn = table_data["%Отношение"].mean()

        table_data["Знаменатель"]= (Rf - table_data[table_data["%Отношение"] > Rf]["%Отношение"]) ** 2  # Для знаменателя разность стандартной доходности и реальной возведенна в квадра
        """""""""
        insert_excel(table_data.reset_index()[
                         ["Open time", "High", "Low", "Open", "Close", "стоим.актив", "Кол-во актива", "%Отношение"]],
                     "A1","Сортино" )
        """""

        profitability = table_data["Знаменатель"].sum()/len(Candle_close)# Среднеее значение по разности доходности для знаменателя
        sortino = (srednee_znac_dohodn - Rf) / (profitability ** (1 / 2))
        return round(sortino,5)

    def fun_sharp_(self, table_data: pd.DataFrame):
        """Нахождение значения коэф шарпа пока без atr"""
        print(self.start_traiding_date)

        # table_data=table_data[pd.to_datetime(table_data.index).dt.date >= self.start_traiding_date]
        table_data = table_data[table_data.index >= pd.to_datetime(self.start_traiding_date)]

        print("----")
        print(table_data)

        # Банковская доходность в процентах
        Candle_close = table_data[["стоим.актив"]]
        print(Candle_close.shift(-1))
        table_data["Сдвиг_close"] = Candle_close.shift(-1)
        table_data["% Отношение"] = (Candle_close / Candle_close.shift(1) - 1) * 100
        # $table_data = table_data[:-2]
        srednee_znac_dohodn = table_data["% Отношение"].mean()

        Rf = self.standart_dohodn / 360  # доходность дневная без рисковая
        standart_dev = table_data["% Отношение"].std(skipna=True)  # Стандартное отклонение
        """""""""
        insert_excel(table_data.reset_index()[
                         ["Open time", "High", "Low", "Open", "Close", "стоим.актив", "Кол-во актива", "% Отношение","Сдвиг_close"]],
                     "A1", "sharp")
                     """""
        print("Средн знач дох", srednee_znac_dohodn, "Станд откл", standart_dev)
        sharp = (srednee_znac_dohodn - Rf) / standart_dev  # Через стандартное отклонение
        print(f"-----{table_data['% Отношение']}---------")
        return round(sharp, 4)

    def _dey_changer(self):
        self.data_tb.set_index("Open time", inplace=True)
        self.data_tb["стоим.актив"] = 0  # Заполняем новую колонку нулями
        print(self.data_tb.index)
        for day in self.data_tb.index:
            self.signal = self.data_tb.loc[day, 'signal']  # Cигнал за день
            self.__next_day = (datetime.timedelta(1))
            self.__next_day = self.__next_day + day
            self.data_tb.loc[day, "стоим.актив"] = self.portf.port_cost
            self.data_tb.loc[day, "Кол-во актива"] = self.portf.free
            try:
                print(self.data_tb.loc[[day], :][["Close", "signal"]])
                if self.data_tb.loc[
                    self.__next_day, 'Open'] > 0 and self.__next_day > self.start_traiding_date:  # Установить дату откуда считать
                    self._sell_by_test()
            except KeyError:
                None

        # self.data_tb.loc[self.__next_day, "стоим.актив"] = self.portf.port_cost
        print(self.data_tb[['стоим.актив', 'sharp']])
        self.sharpa = self.fun_sharp_(self.data_tb)
        self.sortino = self.fun_sortino_(self.data_tb)
        # self.portfel_cost = self.portf.balance + self.free * self.data_tb.loc[day, "Open"]  # Стоимость портфеля
        print("--Шарпа-", self.sharpa)
        print("--Сортино",self.sortino)

    def _sell_by_test_1(self):

        """Модуль запуска выстановки ордеров в зависимости от сигнала
        Основной вариант
        """
        price = self.data_tb.loc[self.__next_day, "Open"]  # Цена
        self.portf.price = price
        need_cost = self.portf.port_cost * self.signal
        count_change = need_cost / price - self.portf.free  # количество изменяемое
        if (0.95 > self.signal > self.porog_by):
            print("создание ордера")
            self.portf.free = count_change
        elif self.signal < self.porog_by:
            self.portf.free -= self.free
        elif self.signal > 0.95 and self.portf.free > 0:
            self.portf.free -= self.free

    def _sell_by_test(self):

        """Модуль запуска выстановки ордеров в зависимости от сигнала
        Основной вариант
        """
        price = self.data_tb.loc[self.__next_day, "Open"]  # Цена
        self.portf.price = price
        need_cost = self.portf.port_cost * self.signal
        count_change = need_cost / price - self.portf.free  # количество изменяемое
        if (self.signal > self.porog_by):
            print("создание ордера")
            self.portf.free = count_change

        elif self.signal < self.porog_by:
            self.portf.free -= self.free

    def _sell_by_test_old(self):

        """
        TEST при разных вариантах порогов

        Модуль запуска выстановки ордеров в зависимости от сигнала"""
        self.porog_by = -0.5

        price = self.data_tb.loc[self.__next_day, "Open"]  # Цена
        self.portf.price = price
        need_cost = self.portf.port_cost * -self.signal
        count_change = need_cost / price - self.portf.free  # количество изменяемое
        if (self.signal < self.porog_by):
            print("создание ордера")
            self.portf.free = count_change
        elif self.signal > 0.95 and self.portf.free > 0:
            self.portf.free -= self.free

    def _sell_by_old(self):

        """Модуль запуска выстановки ордеров в зависимости от сигнала"""
        price = self.data_tb.loc[self.__next_day, "Open"]  # Цена
        self.portf.price = price
        need_cost = self.portf.port_cost * self.signal
        count_change = need_cost / price - self.portf.free  # количество изменяемое
        if (self.signal > self.porog_by):
            print("создание ордера")
            self.portf.free = count_change
        elif self.signal < self.porog_by and self.portf.free > 0:
            self.portf.free -= self.free


def fu_znach_find():
    """Нахождение возможных значений весов
    :return [[],[],[],]
    """
    a = []
    _list = [0.15, 0.2, 0.25, 0.3, 0.35, 0.40, 0.45, 0.5, 0.55, 0.6, 0.8]
    # _list = [0.2, 0.25, 0.35]
    for i in permutations(_list, 3):
        if sum(i) == 1:
            a.append(i)
    print(a)
    print(len(a))
    return a


def main(asset, znach_find, porog: int):
    """

    :param asset:
    :param znach_find:
    :param porog:  Пороговое значение если на задано находит все в интервале
    :return:
    """
    global bal
    znach_doh = []
    index = []
    sharp = []
    final = pd.DataFrame(columns=["n", "Параметры wk", "Баланс", "Шарпа","Сортино"])

    for n in ([8]):  # "Периоды таймфреймов
        date_tb.n = n
        for x1, x2, x3 in znach_find:
            date_tb.wk = {0: x1, 1: x2, 2: x3}
            date_tb.fun_graf_delta(asset)  # Передаем значение в класс
            if porog == None:
                porog_ = arange(0, 10, 1)
            else:
                porog_ = [porog*10]

            for x in porog_:
                porog_by = x / 10
                bal = balance(date_tb.base, porog_by)
                index = ([f"{round(x1, 2)}_{round(x2, 2)}_{round(x3, 2)}"])
                # znach_doh.extend([bal.portf.port_cost])
                znach_doh = bal.portf.port_cost
                sharp = bal.sharpa
                sortino = bal.sortino
                print(index)
                print(znach_doh)
                final = final.append(
                    {"n": n, "Параметры wk": index, "Баланс": znach_doh, "Шарпа": sharp,"Сортино":sortino,"Порого": porog_by},
                    ignore_index=True)
                print(final)

    analiz_max = final["Шарпа"].max()
    select = (final["Шарпа"] == analiz_max)
    select = final[select]

    analiz_max = final["Сортино"].max()
    select2 = (final["Сортино"] == analiz_max)
    select2 = final[select2]


    print(final)
    print("Найденное знач по Шарпу\n", select, asset)
    print("Найденное знач по Сортино\n", select2, asset)
    print(bal.free, bal.portf.port_cost)
    return bal.free, bal.portf.port_cost


if __name__ == "__main__":
    # data_tb = read_csv_test_()
    # print(data_tb)
    # portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    # volume_usdt = balance_mod.volume_usdt
    asset = "RUB=X"
    asset = "BZ=F"
    date_tb = graf_delta_cls(1000, asset)
    analiz = pd.DataFrame()

    znach_find = [[0.25, 0.4, 0.35]]
    znach_find = [[0.15, 0.45, 0.4]]  # Для рубля
    znach_find = [[0.2, 0.45, 0.35]]  # Для нефть
    znach_find = [[0.15, 0.25, 0.6]]

    znach_find = fu_znach_find()  # Включить если надо найти все коэффициенты
    main(asset, znach_find, porog=None)# Если порог не указать будет искать порог где шарпа будет наибольший , порог в интвервале от 0 до 1
