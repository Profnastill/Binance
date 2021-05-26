"""Модуль тестировки торговой стратегии"""

from datetime import date

import pandas as pd
import xlwings as xw


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

    last_signal_table = last_signal_table.set_index(["Open time"])
    print(last_signal_table)
    last_signal_table.reset_index(inplace=True, drop=True)
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


class balance():
    def __init__(self, balance, data_table: pd.DataFrame):
        self.balance = balance
        self.data_tb = data_table
        self.free=pd.DataFrame()
        self.comissia=3#Комиссия в процентах

    def _dey_changer(self):

        for day in self.data_tb.head():
            self.signal = self.data_tb.loc[day, 'Siganl'].values  # Cигнал за день
            self.current_day = self.data_tb.loc[day].shift(1)  # Для следующего дня принятия решеня
            self._sell_by()

    def make_order(self, by_sell):

        if by_sell == "by" and self.balance > 0:
            self.free = self.signal * self.balance / self.current_day["open"].values  # Купленное количесвто
            self.balance -= self.signal * self.balance # Уменьшаем баланс на величину стоимости покупки
        elif by_sell=="sell" and self.free>0:
            self.free


    def _sell_by(self, data: pd.DataFrame):
        self.signal
        if self.signal > 0.5 and self.balance > 0:
            self.make_order("by")
        elif self.signal<0.5 and self.free>0:
            self.make_order("sell")



if __name__ == "__main__":
    data_tb = read_csv_test_()
    test_module2(data_tb)
