"""Расчет по новой технологии машин обучения
 Попытка решения через скользящие срдении
https://habr.com/ru/company/ods/blog/323730/
"""
import math
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fbprophet import Prophet
from plotly.subplots import make_subplots
from scipy import stats

# pip install pyeviews
import get_data_Yahoo
from find_sharp_sortino import insert_excel
from find_sharp_sortino import take_data_candle, ask_input

pd.options.display.max_rows = 25
pd.options.display.max_columns = 15
pd.options.display.expand_frame_repr = False

fig = go.Figure()


class graf_profnet_cls:
    """
    profnet -стартовая функция.

    Функция предсказания .

    base-база даннных для конкретного инструмента.

    self.wk:dict  {0: 0.15, 1: 0.35, 2: 0.50} -Веса для скользящих средних.

    self.n:int = 8-базовый дневной интервал для скользящих средних.

    Параметр asset нужен только тогда когда для одного инструмента создаем конструктор

    """
    error_tab = pd.DataFrame(columns=["Asset", 'MAPE %', 'MAE'])
    counter = 0  # Счетчик срабатываний

    def __init__(self, day_interval, asset: str = 'BTC'):
        self.__day_interval = day_interval
        self.asset = asset
        # self._chooise_find()
        self.__tcur_time = date.today()
        self.day_delta = timedelta(0)  # Временной отступ для оценки прогноза.
        self.__tcur_time = date.today() - self.day_delta
        self.__find_candel_table(asset)  # Функция поиска дневных моделей по имени инструмента
        self.testirovanie = False
        self.predictions = 6  # количество дней прогноща

    def __find_candel_table(self, asset: str, day=None):
        """Функция  нахождения данных для свечных моделей"""
        # print(asset)
        candel_tb = take_data_candle(asset, self.__day_interval, day)  # Получаем набор свечей для asset
        # print("-----------\n", candel_tb)
        # Запускаем попытку поиска на YHOO
        if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
            candel_tb = get_data_Yahoo.yhoo_data_taker(asset,
                                                       self.__day_interval)  # Попытка получить набор свечей с Yhoo
        self.__candel_tb = candel_tb
        return self.__candel_tb  # Возвращает таблицу с с данными по свечам

    def invboxcox(self, y, lmbda):
        if lmbda == 0:
            return (np.exp(y))
        else:
            return (np.exp(np.log(lmbda * y + 1) / lmbda))

    def norm_y(self, table: pd.Series, n):
        """
        Функция построения EWA
        n: Период

        :return:8754210
        """
        table: pd.Series
        #        self.table_mean = table.rolling(window=2).mean()
        halflife = math.log(0.5) / math.log(1 - 1 / n)
        print("halflife=", halflife)

        ewm_new = pd.Series.ewm(table, halflife=halflife, adjust=False).mean()
        print(ewm_new)
        return ewm_new

    def norm_raspr(self, table: pd.Series):
        """"Функция плотности нормального распределения"""
        std = table.std()
        mat_ogid = table.mean()
        norm = (1 / std * pow(2 * 3.142, 0.5)) * 2.718 ** -((table - mat_ogid) ** 2) / (2 * std ** 2)
        return norm

    def fun_profnet_test0(self):
        """"
        Функция прогнозирования
        с попыткой нормализовать последовательность
        """

        table = self.__candel_tb.reset_index()
        table: pd.DataFrame
        if len(table) < 30:
            return
        table = table.rename({'Open time': 'ds', 'Close': 'y'}, axis=1)
        print(table[-10::])
        table["Close"] = table["y"]
        ewm1 = self.norm_y(table['y'], 15)
        ewm2 = self.norm_y(table['y'], 60)
        table["разм_с"] = table["High"] - table['Low']
        table["тело_с"] = (table["Open"] - table['Close']) / table['Close']
        print(table)
        interval = 50
        std_svech = table["тело_с"].tail(interval).std()
        table["свечи_средние"] = self.norm_y(table["тело_с"], interval)
        table["volume_средн"] = table["Volume"].rolling(window=interval).mean()
        std_volume = table["Volume"].tail(interval).std()

        std_svech = abs(table["свечи_средние"] / std_svech)
        std_svech = std_svech.rolling(window=interval * 2).mean() / std_svech.tail(interval * 2).std()

        table2 = table.query("свечи_средние > 3")

        norm_ = self.norm_raspr((table["Close"] - table["Close"].shift(-1)) / table["Close"].shift(-1))

        from scipy.stats import norm
        # norm_ = norm.rvs(size=1000)

        fig = make_subplots(rows=4, cols=1)
        fig.add_trace(go.Scatter(x=table.ds, y=std_svech, name="свечи", mode="lines"), 1, 1)
        fig.add_trace(go.Scatter(x=table.ds, y=table["volume_средн"] / std_volume * 10, name="Объем", mode="lines"), 2,
                      1)
        fig.add_trace(go.Scatter(x=table.ds, y=table["Close"], name="Цены", mode="lines"), 3, 1)
        print(norm)
        fig.add_trace(go.Histogram(x=norm_, name="Нормальнье распеределение"), 4, 1)

        fig.update_layout(title="График", yaxis_title='singnal')
        fig.show()

        stand_dev = table['y'].tail(253).std()  # берет последние значения

        # table['y']=(ewm1-ewm2)/stand_dev

        table['std Close'] = table['Close'].tail(15).std()
        table['y'] = ewm1
        table['y'] = std_svech
        # table['std(y)']=table['y'].tail(15).std()
        # table['y']= table['y'].rolling(window=253).std()

        if self.testirovanie == False:
            trainf = table
        else:
            trainf = table[:-self.predictions:]  # Если тестирование прогноза то включить

        trainf = trainf[['ds', 'y']]

        print(trainf)
        m = Prophet(daily_seasonality=True, yearly_seasonality=True)
        m.fit(trainf)
        holidays = 0  # Нужно для исключения из стратегии
        future = m.make_future_dataframe(periods=self.predictions)
        forecast = m.predict(future)
        print(', '.join(forecast.columns))
        # print(forecast)
        table['ds'] = pd.DatetimeIndex(table['ds'])
        forecast['ds'] = pd.DatetimeIndex(forecast['ds'])
        print(table['ds'].dtypes, forecast['ds'].dtypes)
        print(forecast.set_index('ds'))

        cmp_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(table.set_index('ds'), on='ds')
        # cmp_df=forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].merge(table.set_index('ds')[['y']],on='ds',how='outer')
        # cmp_df['yhat']=cmp_df['yhat']*stand_dev
        # cmp_df['y'] = cmp_df['y'] * stand_dev
        print(f"--------------{asset}--------------------")
        print(cmp_df[-self.predictions - 10::1])
        cmp_df['e'] = cmp_df['y'] - cmp_df['yhat']
        cmp_df['p'] = 100 * cmp_df['e'] / cmp_df['y']
        print(('MAPE %', np.mean(abs(cmp_df[-self.predictions:]['p']))))
        print(('MAE', np.mean(abs(cmp_df[-self.predictions:]['e']))))
        print(f"Время начала отчета = {self.__tcur_time - timedelta(self.predictions)}")
        print(type(np.mean(abs(cmp_df[-self.predictions:]['p'])).astype(float)))
        error_tab1 = pd.DataFrame({"Asset": self.asset, 'MAPE %': [np.mean(abs(cmp_df[-self.predictions:]['p']))],
                                   'MAE': [np.mean(abs(cmp_df[-self.predictions:]['e']))]})
        self.add_table(error_tab1)
        #  plt.show()
        print(self.error_tab)

    def fun_profnet_test1(self):
        """"
        Функция прогнозирования
        с попыткой нормализовать последовательность
        """

        table = self.__candel_tb.reset_index()
        table: pd.DataFrame
        if len(table) < 30:
            return
        table = table.rename({'Open time': 'ds', 'Close': 'y'}, axis=1)

        table["Close"] = table["y"]
        table["Прирост"] = table["Close"].diff()
        uskorenie = (table["Прирост"].shift(1) - table["Прирост"]).tail(1) / 2
        prirost = table["Прирост"].mean()
        # table["Прирост"]=table["Прирост"].mean()
        print(table[-10::])
        table['std(close)'] = table['Close'].tail(15).std()
        table['y'] = table["y"].rolling(window=15).mean()
        table['std(y)'] = table['y'].tail(15).std()
        # table['y']=(ewm1-ewm2)/stand_dev
        # table['y']= table['y'].rolling(window=253).std()

        if self.testirovanie == False:
            trainf = table
        else:
            trainf = table[:-self.predictions:]  # Если тестирование прогноза то включить

        trainf = trainf[['ds', 'y']]

        print(trainf)
        m = Prophet(daily_seasonality=True, yearly_seasonality=True)
        m.fit(trainf)
        holidays = 0  # Нужно для исключения из стратегии
        future = m.make_future_dataframe(periods=self.predictions)
        forecast = m.predict(future)
        print(', '.join(forecast.columns))
        # print(forecast)

        table['ds'] = pd.DatetimeIndex(table['ds'])
        forecast['ds'] = pd.DatetimeIndex(forecast['ds'])
        print(table['ds'].dtypes, forecast['ds'].dtypes)
        print(forecast.set_index('ds'))

        cmp_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(table.set_index('ds'), on='ds')
        # cmp_df=forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].merge(table.set_index('ds')[['y']],on='ds',how='outer')
        # cmp_df['yhat']=cmp_df['yhat']*stand_dev
        # cmp_df['y'] = cmp_df['y'] * stand_dev
        print(f"--------------{asset}--------------------")
        print(cmp_df[-self.predictions - 10::1])
        cmp_df['e'] = cmp_df['y'] - cmp_df['yhat']
        cmp_df['p'] = 100 * cmp_df['e'] / cmp_df['y']
        print(('MAPE %', np.mean(abs(cmp_df[-self.predictions:]['p']))))
        print(('MAE', np.mean(abs(cmp_df[-self.predictions:]['e']))))
        print(f"Время начала отчета = {self.__tcur_time - timedelta(self.predictions)}")
        print(type(np.mean(abs(cmp_df[-self.predictions:]['p'])).astype(float)))
        error_tab1 = pd.DataFrame({"Asset": self.asset, 'MAPE %': [np.mean(abs(cmp_df[-self.predictions:]['p']))],
                                   'MAE': [np.mean(abs(cmp_df[-self.predictions:]['e']))]})
        self.add_table(error_tab1)
        #  plt.show()
        print(self.error_tab)

    def fun_profnet_test2(self):
        """"
        Функция прогнозирования
        с попыткой нормализовать последовательность
        """

        table = self.__candel_tb.reset_index()
        table: pd.DataFrame
        if len(table) < 30:
            return
        table = table.rename({'Open time': 'ds', 'Close': 'y'}, axis=1)
        print(table[-10::])
        table['y'] = table['y'].rolling(window=15).max()  # Агрегируем функции'
        # table=table[15::15]
        print("------------------")
        print(table)

        if self.testirovanie == False:
            trainf = table
        else:
            trainf = table[:-self.predictions:]  # Если тестирование прогноза то включить

        trainf = trainf[['ds', 'y']]

        print(trainf)
        m = Prophet(daily_seasonality=True, yearly_seasonality=True)
        m.fit(trainf)
        holidays = 0  # Нужно для исключения из стратегии
        future = m.make_future_dataframe(periods=self.predictions)
        forecast = m.predict(future)
        print(', '.join(forecast.columns))
        # print(forecast)

        table['ds'] = pd.DatetimeIndex(table['ds'])
        forecast['ds'] = pd.DatetimeIndex(forecast['ds'])
        print(table['ds'].dtypes, forecast['ds'].dtypes)
        print(forecast.set_index('ds'))

        cmp_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(table.set_index('ds'), on='ds')
        # cmp_df=forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].merge(table.set_index('ds')[['y']],on='ds',how='outer')
        # cmp_df['yhat']=cmp_df['yhat']*stand_dev
        # cmp_df['y'] = cmp_df['y'] * stand_dev
        print(f"--------------{asset}--------------------")
        print(cmp_df[-self.predictions - 10::1])
        cmp_df["new"] = cmp_df['y'][:-self.predictions:]
        cmp_df['e'] = cmp_df['y'] - cmp_df['yhat']
        cmp_df['p'] = 100 * cmp_df['e'] / cmp_df['y']
        print(('MAPE %', np.mean(abs(cmp_df[-self.predictions:]['p']))))
        print(('MAE', np.mean(abs(cmp_df[-self.predictions:]['e']))))
        print(f"Время начала отчета = {self.__tcur_time - timedelta(self.predictions)}")
        print(type(np.mean(abs(cmp_df[-self.predictions:]['p'])).astype(float)))
        error_tab1 = pd.DataFrame({"Asset": self.asset, 'MAPE %': [np.mean(abs(cmp_df[-self.predictions:]['p']))],
                                   'MAE': [np.mean(abs(cmp_df[-self.predictions:]['e']))]})
        self.add_table(error_tab1)
        #  plt.show()
        print(self.error_tab)

    def fun_profnet_boksa_1(self):
        """"
        Функция прогнозирования

        c реаизацией бокса кокса
        """

        table = self.__candel_tb.reset_index()
        if len(table) < 30:
            return
        table = table.rename({'Open time': 'ds', 'Close': 'y'}, axis=1)
        print(table[-10::])
        print(table)

        if self.testirovanie == False:
            trainf = table
        else:
            trainf = table[:-self.predictions:]  # Если тестирование прогноза то включить

        trainf = trainf[['ds', 'y']]
        trainf['y'], lmbda_prophet = stats.boxcox(trainf['y'])

        print(trainf, lmbda_prophet)
        m = Prophet(daily_seasonality=True, yearly_seasonality=True)
        m.fit(trainf)
        holidays = 0  # Нужно для исключения из стратегии
        future = m.make_future_dataframe(periods=self.predictions)
        forecast = m.predict(future)
        print(', '.join(forecast.columns))
        # print(forecast)
        table['ds'] = pd.DatetimeIndex(table['ds'])
        forecast['ds'] = pd.DatetimeIndex(forecast['ds'])

        forecast['yhat'] = self.invboxcox(forecast.yhat, lmbda_prophet)
        forecast['yhat_lower'] = self.invboxcox(forecast.yhat_lower, lmbda_prophet)
        forecast['yhat_upper'] = self.invboxcox(forecast.yhat_upper, lmbda_prophet)

        print(forecast.set_index('ds'))
        cmp_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(table.set_index('ds'), on='ds')
        print(f"--------------{asset}--------------------")
        print(cmp_df[-self.predictions - 10::1])

        cmp_df['e'] = cmp_df['y'] - cmp_df['yhat']
        cmp_df['p'] = 100 * cmp_df['e'] / cmp_df['y']
        print(('MAPE %', np.mean(abs(cmp_df[-self.predictions:]['p']))))
        print(('MAE', np.mean(abs(cmp_df[-self.predictions:]['e']))))
        print(f"Время начала отчета = {self.__tcur_time - timedelta(self.predictions)}")

        if (1 - cmp_df["yhat"][-self.predictions - 10:].mean(axis=0) / cmp_df["y"][-self.predictions - 10:].mean(
                axis=0)) * 100 < 8:
            sredn = cmp_df["yhat"][-self.predictions:].mean(axis=0)
            minimal_teku = cmp_df["y"].iloc[-self.predictions - 1]
            dinamika = (1 - minimal_teku / sredn) * 100
        else:
            dinamika = "None"

        error_tab1 = pd.DataFrame({"Asset": self.asset, 'MAPE %': [np.mean(abs(cmp_df[-self.predictions:]['p']))],
                                   'MAE': [np.mean(abs(cmp_df[-self.predictions:]['e']))], 'Динамика': dinamika})
        self.add_table(error_tab1)
        #  plt.show()
        print(self.error_tab)

    @classmethod
    def add_table(cls, table: pd.DataFrame):
        cls.error_tab = cls.error_tab.append(table)
        return cls.error_tab

    @property
    def get_table(self):
        return self.error_tab


if __name__ == '__main__':
    table = ask_input()
    # tableable = table[0:2]
    # ВНИМАНИЕ! строкой ниже Биток должен быть всегда первыми иначе фильтр работать не будет
    base_table = pd.DataFrame(
        {'asset': ['BTC', 'BNB', 'DX-Y.NYB', "GC=F", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table: pd.DataFrame = pd.concat([base_table, table], ignore_index=True,
                                    sort=False)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    print(base_table)
    day = 720  # Дни поиска
    table = table[1:2]

    for asset in table['asset']:
        start = graf_profnet_cls(day, asset)
        start.predictions = 15  # Время прогнозирования
        start.testirovanie = True  # ТЕСТИРОВАНИЕ ИЛИ True- да тестируем Else прогнозируем

        # start.fun_profnet()
        start.fun_profnet_test0()
        # start.fun_profnet_boksa()

    counter = 1
    insert_excel(start.get_table, f'A{counter}', 'Отклонение')
