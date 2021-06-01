"""Модуль проверки по сигналу на основе скользящего среднего, так же строим графики свечей"""
import math
# import stocker
import time
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import find_sharp_sortino as ssf
import get_data_Yahoo
# import dash
from find_sharp_sortino import take_data_candle, ask_input

fig = go.Figure()  # Создаем график
columns = ['asset', 'signal']
index = [0, 0]
last_signal = pd.DataFrame(columns=columns, index=[0, 0])  # Пустая таблица для добавления в нее данных


# btc_table= pd.DataFrame(columns=columns)#Пустая таблица для хранения данных по биткоину чтобы использовать их как фильтр
# print(last_signal)


def write_base_csv(asset, table):
    """Запись тестовой базы данных день сигнал цена закрытия """
    if asset == "BZ=F":
        table.to_csv(f'B:/download/test_base_BTC.csv', index_label='Open time')
        return
    else:
        return


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

    def __init__(self, day_interval, asset:str='BTC'):
        self.__day_interval = day_interval
        # self._chooise_find()
        self.__tcur_time = date.today()
        self.day = timedelta(1)
        self.__tcur_time = date.today() - self.day
        self.__find_candel_table(asset)# Функция поиска дневных моделей по имени инструмента


        self.n = 8
        self.__n1 = [self.n, self.n * 2, self.n * 4]  # Коэффициент количество дней для сколь средней
        self.__n2 = [self.n * 3, self.n * 6, self.n * 12]
        self.last_signal = pd.DataFrame(columns=['asset', 'signal'], index=[0, 0])
        self.wk = {0: 0.15, 1: 0.35, 2: 0.50}  # Веса для скользящих средних

        # self._chooise_find()

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
        # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя

        if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
            candel_tb = get_data_Yahoo.yhoo_data_taker(asset,
                                                       self.__day_interval)  # Попытка получить набор свечей с Yhoo
            print(candel_tb[:5])
            if len(candel_tb) < 30:
                return

        # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
        for i in range(len(self.__n1)):
            name_1 = str(self.__n1[i])
            name_2 = str(self.__n2[i])
            candel_tb['EWA1-' + name_1] = self._ema_f(candel_tb, self.__n1[i])  # Эксопненциальная скользящая средняя №1
            candel_tb['EWA2-' + name_2] = self._ema_f(candel_tb, self.__n2[i])  # Эксопненциальная скользящая средняя №2
        grapf(candel_tb, asset)
        return candel_tb

    def __choice_find(self, table: pd.DataFrame):
        """Выбор что найти хотим"""
        inp = input("выберите что ищем:  1- сигнал 2-график")
        if int(inp) == 1:
            table.apply(lambda x: self.start(x.asset), axis=1)#Вызов комбинарота
        elif int(inp) == 2:
            table.apply(lambda x: self._fun_ewa(x.asset), axis=1)
        else:
            return self.__choice_find(table)

    def start(self,asset):
        "Комбинатор функция для одновременного вызова"
        self.__find_candel_table(asset)
        self._fun_graf_delta(asset)

    def __find_candel_table(self, asset:str, day=None):
        """Функция построения эксп скол средней. и нахождение сигнала покупки и продажт"""
        print(asset)
        candel_tb = take_data_candle(asset, self.__day_interval, day)  # Получаем набор свечей для asset
        print("-----------\n",candel_tb)
        # Запускаем попытку поиска на YHOO
        # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
        if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
            candel_tb = get_data_Yahoo.yhoo_data_taker(asset,
                                                       self.__day_interval)  # Попытка получить набор свечей с Yhoo
            print(candel_tb[:5])
            if len(candel_tb) < 30:
                return
        print(candel_tb["Open time"][-1::].values, self.__tcur_time)
        print(self.__tcur_time - timedelta(3))
        if candel_tb["Open time"][-1::].values == np.datetime64(self.__tcur_time - timedelta(
                3)):  # Отсеиваем элементы для которых по какой то причине данные не сооответствуют тек дню
            return
        self.__candel_tb=candel_tb
        return self.__candel_tb #Возвращает таблицу с с данными по свечам

    def _fun_graf_delta(self,asset):
        self.__candel_tb['signal'] = 0
        base_candel = pd.DataFrame()
        for i in range(len(self.__n1)):
            name_1 = str(self.__n1[i])  # получаем имя для графика
            name_2 = str(self.__n2[i])
            self.__candel_tb['EWA1-' + name_1] = self._ema_f(self.__candel_tb, self.__n1[i])  # Эксопненциальная скользящая средняя №1
            self.__candel_tb['EWA2-' + name_2] = self._ema_f(self.__candel_tb, self.__n2[i])  # Эксопненциальная скользящая средняя №2
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


        #self.__candel_tb['Удар'] = self.__filter_signal(self.__candel_tb[['asset', 'signal']][-2::1])  # Запускаем функцию рассматриваем только два дня
        self.__candel_tb['Удар']=0# временно отключим
        self.__candel_tb['sharp'] = ssf.fun_sharp_(self.__candel_tb[-14::1])
        self.__candel_tb['sortino'] = ssf.fun_sharp_(self.__candel_tb[-14::1])

        self.last_signal = pd.concat(
            [self.last_signal, self.__candel_tb[["Open time", 'asset', 'signal', 'Удар', 'sharp', 'sortino']][-1::]],
            ignore_index=True)  # Таблица имя инструмента/сигнал для заполнения
        self.__graf_show(self.__candel_tb, asset)  # вызыв функции заполнения данных для графика
        return self.last_signal

    def __graf_show(self, candel_tb, asset):
        # данные для отображения графиков
        fig.add_trace(go.Scatter(x=candel_tb['Open time'], y=candel_tb['signal'], name=asset,
                                 mode='lines'))  # Обновление для графиков
        fig.update_layout(title="График_импульса", yaxis_title='singnal')

    def grafics_show(self):
        # Отображает график
        fig.show()

    def filter(self):
        # Фильтр выборки для УДара по значению сигнала
        self.last_signal.dropna(how='all', inplace=True)
        self.last_signal.sort_values(by=['signal'], inplace=True)
        select_2 = self.last_signal.query('(Удар == "UP") | (Удар == "Down")')
        return select_2

    def __filter_signal(self, signal):
        """Фильтр по коэффициенту signal.
         Находит инстрменты которые пробили Биткоин
         Принимает название инструмента и таблицу сигналов """
        test_p = None
        signal = signal.reset_index(drop='index')
        # print("signal insert table \n", signal)
        global btc_table
        if signal['asset'].values[0] == 'BTC':  # Сохранения данных для Битка для использования его как фильтр
            btc_table = signal.copy(deep=True).reset_index()
            btc_table.reset_index(inplace=True)
            print("BTC table \n", signal, )
            test_p = 0
            return
        else:
            x4 = btc_table['signal'].iloc[1]  # последний
            x3 = btc_table['signal'].iloc[0]
            x1 = signal['signal'].iloc[0]
            x2 = signal['signal'].iloc[1]  # последний
            if x1 < x3 and x2 > x4:
                test_p = "UP"
            elif x1 > x3 and x2 < x4:
                test_p = "Down"
            else:
                test_p = None
        return test_p


def input_enter():
    enter = input('Нажмите enter')
    if enter == '':
        return
    else:
        return input_enter()


def grapf(table, assetname):
    """Функция построения графиков для необходимых инструментов"""
    # layot=(paper_bgcolor='rgb(141,238,238)', linecolor='#636363']
    fig = go.Figure(data=[go.Candlestick(x=table['Open time'],
                                         open=table['Open'],
                                         high=table['High'],
                                         low=table['Low'],
                                         close=table['Close']),
                          go.Scatter(x=table['Open time'], y=table['EWA1-8'], line=dict(color='red', width=1)),
                          go.Scatter(x=table['Open time'], y=table['EWA2-24'], line=dict(color='orange', width=1))])
    fig.update_layout(title=assetname, yaxis_title='price')
    #
    fig.show()
    time.sleep(5)


def insert_csv(table, name: str):
    """Сохдание файла базы"""
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


if __name__ == '__main__':
    table = ask_input()
    # tableable = table[0:2]
    # ВНИМАНИЕ! строкой ниже Биток должен быть всегда первыми иначе фильтр работать не будет
    base_table = pd.DataFrame({'asset': ['BTC', 'DX-Y.NYB', "GOLD", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table: pd.DataFrame = pd.concat([base_table, table], ignore_index=True,
                                    sort=False)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    print('Таблица c позициями \n', table)
    day = 360  # Дни поиска
    start = graf_delta_cls(day)
    # start._chooise_find()  # Запуск выбора что таблиц поиска Изменяет в глобальном пространстве имен lastsignal
    #start.grafics_show()
    BTC = graf_delta_cls(day)
    BTC._fun_graf_delta("XLM")
    print(BTC.base)

    #    insert_csv(last_signal, "all_find_signal")  # Тут вставляем всю таблицу обновляем базу данных

    # transfer_data(last_signal)  # Данные в список  для yhooo
    print('END')
    # table.apply(lambda x:take_data_candle(x.asset,10),axis=1)