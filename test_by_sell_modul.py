"""Модуль тестировки торговой стратегии"""
import datetime
from datetime import date
from itertools import *


import pandas as pd
import xlwings as xw

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


def test_module(data_tb):
    """Функция для тестирования системы по дням"""
    xlbook = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
    sheet = xlbook.sheets('Портфель')
    balance_tb = sheet.range('A1').options(pd.DataFrame, expand='table', index=False).value
    print(balance_tb)


def test_module2(data_tb: pd.DataFrame):
    """Функция для тестирования системы по дням"""
    data_tb.rolling()


class crt_balans:
    def __init__(self):
        self.balance = 10000
        self.free = 0

    def change_balance(self):
        self.balance = 0


class balance():
    def __init__(self, balance, data_table: pd.DataFrame):
        self.balance = balance
        self.data_tb = data_table.copy(deep=True)
        self.free = 0
        self.comissia = 0.1  # Комиссия в процентах
        self._dey_changer()

    def fun_sharp_(self,table_data: pd.DataFrame):
        """Нахождение значения коэф шарпа пока без atr"""
        standart_dohodn = 0
        Candle_close = table_data["стоим.актив"]
        table_data["Доходность шарп"] = Candle_close.diff() / Candle_close.shift(-1)
        srednee_znac_dohodn = table_data["Доходность шарп"].mean()
        Rf = standart_dohodn / 365  # доходность дневная без рисковая
        standart_dev = table_data["Доходность шарп"].std(skipna=True)  # Стандартное отклонение
        sharp = (srednee_znac_dohodn - Rf) / standart_dev  # Через стандартное отклонение
        return round(sharp,3)

    def _dey_changer(self):
        self.data_tb.set_index("Open time", inplace=True)
        self.data_tb["стоим.актив"]=0# Заполняем новую колонку нулями
        for day in self.data_tb.index[0:-1:1]:
            self.signal = self.data_tb.loc[day, 'signal']  # Cигнал за день
            next_day = (datetime.timedelta(1))
            next_day= next_day+day
            print(type(day), day)
            try:
                print([pd.to_datetime( next_day)])

                self.current_day_tb = self.data_tb.loc[
                    [pd.to_datetime(next_day)]]  # Для следующего дня принятия решеня таблица
                print("-+++--")
                print(self.current_day_tb)
                if self.current_day_tb['Open'].values > 0:
                    self._sell_by()

            except KeyError:
                None

            self.data_tb.loc[next_day, "стоим.актив"] = self.balance + self.free * self.data_tb.loc[next_day, "Open"]
        self.data_tb.loc[next_day, "стоим.актив"]=self.balance + self.free * self.data_tb.loc[next_day, "Open"]
        self.sharpa = self.fun_sharp_(self.data_tb)
        self.portfel_cost = self.balance + self.free * self.current_day_tb["Open"].values  # Стоимость портфеля

        print("--Шарпа-",self.sharpa)

    def make_order_0ld(self, by_sell):
        day_cost = self.current_day_tb["Open"].values  # стоимость актива текущая
        print("создание ордера")

        if by_sell == "by" and self.balance > 0:

            count_change = self.signal * self.balance / day_cost  # Купленное количестdо
            self.balance -= count_change * day_cost  # Уменьшаем баланс на величину стоимости покупки
            self.free += count_change - count_change * self.comissia

        elif by_sell == "sell" and self.free > 0:
            print()
            usd_change = self.free * day_cost
            self.free -= self.free
            self.balance += usd_change - usd_change * self.comissia
        else:
            None
        print("_------------------------------------------")

        print(f"{self.current_day_tb.index.tolist()},кол-во= {self.free},стоимость активов={self.balance + self.free * day_cost}")

    def make_order(self,count_change):
        """count_chage = -100 1020"""
        day_cost = self.current_day_tb["Open"].values  # стоимость актива текущая
        print("создание ордера")
        self.balance +=count_change*day_cost
        self.free +=count_change
        if self.signal<0.2:#Если меньше 0.5 продать все активы
            self.balance += self.free * day_cost
            self.free += -self.free
        print(
            f"{self.current_day_tb.index.tolist()},кол-во= {self.free},стоимость активов={self.balance + self.free * day_cost}")

    def _sell_by(self):
        """Модуль запуска выстановки ордеров в зависимости от сигнала"""
        count_in_port = self.balance * self.signal/self.current_day_tb["Open"]-self.free  # Необходимое количество
        if (self.signal > 0.2) & (self.balance > 0) & (count_in_port!=self.free):
            count_change=count_in_port - self.free  # необходимое количество
            self.make_order("by",count_change)




def fu_znach_find():
    """Нахождение возможных значений весов
    :return [[],[],[],]
    """
    a = []
    _list = [0.15, 0.2, 0.25, 0.35, 0.40, 0.45, 0.5, 0.55, 0.6, 0.8]
    # _list = [0.2, 0.25, 0.35]
    for i in permutations(_list, 3):
        if sum(i) == 1:
            a.append(i)
    print(a)
    print(len(a))
    return a


def main(asset, znach_find):
    global bal
    znach_doh = []
    index = []
    sharp=[]
    #final=pd.DataFrame(columns=["n","Параметры wk", "Баланс","Шарпа"],index=[0,0,0])
    final=pd.DataFrame()
    for n  in [2,4,8]:
        for x1, x2, x3 in znach_find:
            date_tb.wk = {0: x1, 1: x2, 2: x3}
            date_tb._fun_graf_delta(asset)  # Передаем значение в класс
            bal = balance(10000, date_tb.base)
            index.extend([f"{round(x1, 2)}_{round(x2, 2)}_{round(x3, 2)}"])
            znach_doh.extend(bal.portfel_cost)
            print("--ada",bal.sharpa,type (bal.sharpa))
            sharp.extend([bal.sharpa])
            print(index)
            print(znach_doh)
            analiz = pd.DataFrame({"n":n,"Параметры wk": index, "Баланс": znach_doh,"Шарпа":sharp})

        final = final.append(analiz)
    analiz_max = final["Шарпа"].max()
    select = (final["Шарпа"] == analiz_max)
    select = final[select]
    print(analiz)
    print("Найденное знач\n", select)
    print(bal.free, bal.balance)
    return bal.free, bal.balance



if __name__ == "__main__":
    # data_tb = read_csv_test_()
    # print(data_tb)
    # portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    # volume_usdt = balance_mod.volume_usdt
    asset = "BTC"
    date_tb = graf_delta_cls(360, asset)
    analiz = pd.DataFrame()
    znach_find = fu_znach_find()
    znach_find=[[0.15,0.4,0.45],[0.15,0.45,0.4]]
    main(asset,znach_find)
