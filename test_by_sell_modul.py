"""Модуль тестировки торговой стратегии"""
import datetime
from datetime import date

import pandas as pd
import xlwings as xw
#import balance_mod

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
    last_signal_table['Open time']=last_signal_table['Open time'].apply(lambda x:datetime.datetime.strptime(x,"%Y-%m-%d").date())
    last_signal_table = last_signal_table.set_index(["Open time"])
    print(last_signal_table)
    #last_signal_table.reset_index(inplace=True, drop=True)
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
        self.balance=10000
        self.free=0
    def change_balance(self):
        self.balance=0


class balance():
    def __init__(self, balance, data_table: pd.DataFrame):
        self.balance = balance
        self.data_tb = data_table.copy(deep=True)
        self.free=0
        self.comissia=0.1#Комиссия в процентах
        self._dey_changer()

    def _dey_changer(self):
        for day in self.data_tb.index[:-1:]:
            self.signal = self.data_tb.loc[day, 'signal']# Cигнал за день
            next_day=datetime.timedelta(1)
            print(day)

            self.current_day_tb = self.data_tb.loc[[(day + next_day)]]  # Для следующего дня принятия решеня таблица
            print ("---")
            print(self.current_day_tb)
            if self.current_day_tb['Open'].values>0:
                self._sell_by()


    def make_order(self, by_sell):
        day_cost=self.current_day_tb["Open"].values#стоимость актива текущая
        if by_sell == "by" and self.balance > 0:
            count_change = self.signal * self.balance / day_cost  # Купленное количесвто
            self.balance -=count_change *  day_cost # Уменьшаем баланс на величину стоимости покупки
            self.free+=count_change-count_change* self.comissia

        elif by_sell=="sell" and self.signal<0.5 and self.free>0:
            print()
            usd_change = self.free * day_cost
            self.free-=self.free
            self.balance+=usd_change-usd_change* self.comissia
        else:
            None
        print(f"{self.current_day_tb.index.tolist()},кол-во= {self.free},стоимость активов={self.balance+self.free*day_cost}")


    def _sell_by(self):
        self.signal
        if (self.signal > 0.5) | (self.balance > 0):
            self.make_order("by")
        elif (self.signal<0.5) | (self.free>0):
            self.make_order("sell")



if __name__ == "__main__":
    data_tb = read_csv_test_()
    print(data_tb)
    #portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    #volume_usdt = balance_mod.volume_usdt

    bal=balance(10000,data_tb)
    print(bal.free,bal.balance)

