"""Модуль проверки по сигналу на основе скользящего среднего, так же строим графики свечей"""
import math
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import get_data_Yahoo
from find_sharp_sortino import take_data_candle, ask_input, insert_excel, fun_sharp_,fun_sortino_

fig = go.Figure()  # Создаем график
columns = ['asset', 'signal']
index = [0, 0]
last_signal = pd.DataFrame(columns=columns, index=[0, 0])  # Пустая таблица для добавления в нее данных
total_signal=pd.DataFrame(columns=columns, index=[0, 0])# таблица для глобального сигнала




def write_base_csv(asset, table):
    """Запись тестовой базы данных день сигнал цена закрытия """
    if asset == "BZ=F":
        table.to_csv(f'B:/download/test_base_BTC.csv', index_label='Open time')
        return
    else:
        return


class data_tb_save_cls:
    """
    Класс для сборки данных рассчитынных для каждого asset в сборную табличку pandas для всех asset

    insert_xls_file- печать резльтатов в xls файл

    """

    def __init__(self):
        self._table = pd.DataFrame(columns=["Open time", 'asset', 'signal', 'Удар', 'sharp', 'sortino'])

    def table_connect(self, data):
        self._table: pd.DataFrame
        print("--сигналы по инструментам-")
        print(data)
        # self._table=pd.concat(self._table,data,ignore_index=True)
        self._table = self._table.append(data)
        self._table = self._table.reindex()

    def filter(self):
        # Фильтр выборки для УДара по значению сигнала
        self._table.dropna(how='all', inplace=True)
        self._table.sort_values(by=['signal'], inplace=True)
        select_2 = self._table.query('(Удар == "UP") | (Удар == "Down")')
        return select_2

    def insert_xls_file(self):
        """Вставка данных в excel"""
        l = len(self._table)
        insert_excel(self._table, "L1")
        insert_excel(self.filter(), f"L{str(l + 4)}")

    def insert_csv(self):
        """
        
        Вставка символов в csv  для инвестинга

        """
        select = self._table.query('signal > 0.5')
        select['asset'] = select['asset'] + "/USD"
        select['asset'].to_csv(f'B:/download/simvol_sorted.csv', index_label='asset')

    @staticmethod
    def insert_csv_base(table: pd.DataFrame, name: str):
        """Сохдание файла базы для расчета портфеля"""
        table = table.query("asset not in ['BTC', 'DX-Y.NYB', 'GOLD', 'BZ=F', 'RUB=X']")

        inp = input("Нужно ли обновить базу Yes=Y No=any key")

        tcur_time = date.today()
        tcur_time = tcur_time.strftime("%m%d%Y")
        if inp == "Y":

            # table=table['asset']
            table['asset'] = table['asset'] + "/USD"
            table.to_csv(f'B:/download/{str(tcur_time) + name}.csv', index_label='asset')
            return
        else:
            return


data_save = data_tb_save_cls()  # Инициализация класса


class graf_delta_cls:
    """
    _fun_graf_delta-стартовая функция.

    Функция построения графиков по сигналу.

    lastsignal-это итоговая таблица с коэффициентами шарпа и сортино (искомое значение).

    base-база даннных для конкретного инструмента.

    self.wk:dict  {0: 0.15, 1: 0.35, 2: 0.50} -Веса для скользящих средних.

    self.n:int = 8-базовый дневной интервал для скользящих средних.

    Параметр asset нужен только тогда когда для одного инструмента создаем конструктор

    """

    def __init__(self, day_interval, asset: str = 'BTC'):
        self.__day_interval = day_interval
        # self._chooise_find()
        self.__tcur_time = date.today()
        self.day = timedelta(1)
        self.__tcur_time = date.today() - self.day
        self.n = 8
        self.__n1 = [self.n, self.n * 2, self.n * 4]  # Коэффициент количество дней для сколь средней
        self.__n2 = [self.n * 3, self.n * 6, self.n * 12]
        self.wk = {0: 0.4, 1: 0.45, 2: 0.15}  # Веса для скользящих средних
        self.__find_candel_table(asset)  # Функция поиска дневных моделей по имени инструмента

    def _ema_f(self, table, n: int):
        """Функция экспоненциальной EMA нужна для ewa"""
        halflife = math.log(0.5) / math.log(1 - 1 / n)
        # ewm=pd.Series.ewm(table['Close'], alpha=n, halflife=halflife).mean()
        # ewm = pd.Series.ewm(table['Close'], alpha=1 / n).mean()
        ewm = pd.Series.ewm(table['Close'], halflife=halflife).mean()
        return pd.Series(ewm)

    def _fun_ewa(self, asset):
        """Функция построения эксп скол средней."""
        candel_tb = take_data_candle(asset, self.__day_interval)  # Получаем набор свечей
        # Запускаем попытку поиска на YHOO
        print(candel_tb[:5])

        if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
            candel_tb = get_data_Yahoo.yhoo_data_taker(asset,
                                                       self.__day_interval)  # Попытка получить набор свечей с Yhoo
            print(candel_tb[:5])
            if len(candel_tb) < 30:
                return

        for i in range(len(self.__n1)):
            name_1 = str(self.__n1[i])
            name_2 = str(self.__n2[i])
            candel_tb['EWA1-' + name_1] = self._ema_f(candel_tb, self.__n1[i])  # Эксопненциальная скользящая средняя №1
            candel_tb['EWA2-' + name_2] = self._ema_f(candel_tb, self.__n2[i])  # Эксопненциальная скользящая средняя №2
        return candel_tb

    def __find_candel_table(self, asset: str, day=None):
        """Функция  нахождения данных для свечных моделей"""
        print(asset)
        candel_tb = take_data_candle(asset, self.__day_interval, day)  # Получаем набор свечей для asset
        print("-----------\n", candel_tb)
        # Запускаем попытку поиска на YHOO
        # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
        if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
            candel_tb = get_data_Yahoo.yhoo_data_taker(asset,
                                                       self.__day_interval)  # Попытка получить набор свечей с Yhoo
            print(candel_tb[:5])
            if len(candel_tb) < 30:
                self.__candel_tb = pd.DataFrame()
                return
        print(candel_tb["Open time"][-1::].values, self.__tcur_time)
        print(self.__tcur_time - timedelta(3))
        if candel_tb["Open time"][-1::].values == np.datetime64(self.__tcur_time - timedelta(
                3)):  # Отсеиваем элементы для которых по какой то причине данные не сооответствуют тек дню
            self.__candel_tb = pd.DataFrame()
            return
        self.__candel_tb = candel_tb
        return self.__candel_tb  # Возвращает таблицу с с данными по свечам

    def fun_graf_delta(self, asset):
        """функция построения сигнала, принимает в себя названия asset
        Возвращает сигнал для инструмента"""
        if len(self.__candel_tb) == 0:  # Защита если таблица пустая
            return
        self.__candel_tb['signal'] = 0
        base_candel = pd.DataFrame()
        for i in range(len(self.__n1)):
            name_1 = str(self.__n1[i])  # получаем имя для графика
            name_2 = str(self.__n2[i])
            self.__candel_tb['EWA1-' + name_1] = self._ema_f(self.__candel_tb,
                                                             self.__n1[i])  # Эксопненциальная скользящая средняя №1
            self.__candel_tb['EWA2-' + name_2] = self._ema_f(self.__candel_tb,
                                                             self.__n2[i])  # Эксопненциальная скользящая средняя №2
            self.__candel_tb['xk'] = self.__candel_tb['EWA1-' + name_1] - self.__candel_tb['EWA2-' + name_2]
            standert_dev_63 = self.__candel_tb['Close'][-63::1].std()  # Стандартное отклонение 63 дня
            self.__candel_tb['yk'] = self.__candel_tb['xk'] / standert_dev_63
            standert_dev_252 = self.__candel_tb['yk'][-252::1].std()  # Стандартное отклонение 252 дня
            self.__candel_tb['zk'] = self.__candel_tb['yk'] / standert_dev_252
            # print('станд отклонеение', standert_dev_252)
            self.__candel_tb['uk'] = (self.__candel_tb['zk'] * (math.e ** (-(self.__candel_tb['zk'] ** 2) / 4))) / (
                    math.sqrt(2) * math.e ** (-1 / 2))  # Функция реакции
            wk = self.wk[i]  # Веса
            self.__candel_tb['signal'] += wk * self.__candel_tb['uk']  # получения сигнала
            self.__candel_tb['asset'] = asset
            base_candel = pd.concat([base_candel, self.__candel_tb], ignore_index=True)
        self.base = self.__candel_tb  # База данных
        self.__candel_tb['signal'] = self.__candel_tb['signal'].round(2)
        self.__candel_tb['Удар'] = self.__filter_signal()  # временно отключим
        self.__candel_tb['sharp'] = fun_sharp_(self.__candel_tb[-14::1])
        self.__candel_tb['sortino'] = fun_sortino_(self.__candel_tb[-14::1])
        data_save.table_connect(self.__candel_tb[["Open time", 'asset', 'signal', 'Удар', 'sharp', 'sortino']][-1::])

        self.__graf_show(self.__candel_tb, asset)  # вызыв функции заполнения данных для графика
        # return self.last_signal

    def __graf_show(self, candel_tb, asset):
        # данные для отображения графиков

        fig.add_trace(go.Scatter(x=candel_tb['Open time'], y=candel_tb['signal'], name=asset,
                                 mode='lines'))  # Обновление для графиков
        fig.update_layout(title="График_импульса", yaxis_title='singnal')

    def __tota_graf(self, candel_tb, asset):
        new_table=pd.DataFrame()


    @classmethod
    def grafics_show(cls):
        # Отображает график
        fig.show()

    @classmethod
    def last_signals(cls):
        """:return data_save._table"""
        print("Таблица с сигналами \n", data_save._table)
        return data_save._table

    def __filter_signal(self):
        """
        Фильтр по коэффициенту signal.

         Находит инструменты которые пробили уровень 0.5

         Принимает название инструмента и таблицу сигналов
         """
        test_p = None
        signal = self.__candel_tb
        signal = signal.reset_index(drop='index')[-2::1]
        # print("signal insert table \n", signal)
        x1 = signal['signal'].iloc[0]
        x2 = signal['signal'].iloc[1]  # последний
        if x1 < 0.2 and x2 > 0.2:
            test_p = "UP"
        else:
            test_p = None
        return test_p


if __name__ == '__main__':
    table = ask_input()
    # tableable = table[0:2]
    # ВНИМАНИЕ! строкой ниже Биток должен быть всегда первыми иначе фильтр работать не будет
    base_table = pd.DataFrame({'asset': ['BTC', 'DX-Y.NYB', "GC=F", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table: pd.DataFrame = pd.concat([base_table, table], ignore_index=True,
                                    sort=False)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    print(base_table)

    day = 720  # Дни поиска
    # table = table[0:3]
    for asset in table['asset']:
        start = graf_delta_cls(day, asset)
        start.wk = {0: 0.4, 1: 0.45, 2: 0.15}
        start.fun_graf_delta(asset)

    signal_table = graf_delta_cls.last_signals()  # значения последних сигналов
    graf_delta_cls.grafics_show()  # Вывод данных в графики
    data_save.insert_csv_base(signal_table, "all_find_signal")  # Для анализа порфеля
    data_save.insert_csv()  # Обновляет базу по фильтру для investing
    data_save.insert_xls_file()  # вставка данных в excel
    print('END')
