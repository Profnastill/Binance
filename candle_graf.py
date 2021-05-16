"""Модуль проверки по сигналу на основе скользящего среднего, так же строим графики свечей"""
import math
# import stocker
import time

import pandas as pd
import plotly.graph_objects as go

import balance_mod
import dop_data
import find_sharp_sortino as ssf
# import dash
from find_sharp_sortino import take_data_candle, ask_input, insert_excel, transfer_data


def ema_f(table, n):
    """Функция экспоненциальной EMA нужна для ewa"""
    halflife = math.log(0.5) / math.log(1 - 1 / n)
    # ewm=pd.Series.ewm(table['Close'], alpha=n, halflife=halflife).mean()
    # ewm = pd.Series.ewm(table['Close'], alpha=1 / n).mean()
    ewm = pd.Series.ewm(table['Close'], halflife=halflife).mean()
    return pd.Series(ewm)


def fun_ewa(asset, day_interval):
    """Функция построения эксп скол средней."""
    n1 = [8, 16, 32]  # Коэффициент количество дней для сколь средней
    n2 = [24, 48, 96]
    candel_tb = take_data_candle(asset, day_interval)  # Получаем набор свечей
    # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
    for i in range(len(n1)):
        name_1 = str(n1[i])
        name_2 = str(n2[i])
        candel_tb['EWA1-' + name_1] = ema_f(candel_tb, n1[i])  # Эксопненциальная скользящая средняя №1
        candel_tb['EWA2-' + name_2] = ema_f(candel_tb, n2[i])  # Эксопненциальная скользящая средняя №2
    grapf(candel_tb, asset)
    return candel_tb


fig = go.Figure()  # Создаем график

columns = ['asset', 'signal']
index = [0, 0]
last_signal = pd.DataFrame(columns=columns, index=[0, 0])  # Пустая таблица для добавления в нее данных


# btc_table= pd.DataFrame(columns=columns)#Пустая таблица для хранения данных по биткоину чтобы использовать их как фильтр

# print(last_signal)


def fun_graf_delta(asset, day_interval):
    """Функция построения эксп скол средней. и нахождение сигнала покупки и продажт"""
    n1 = [8, 16, 32]  # Коэффициент количество дней для сколь средней
    n2 = [24, 48, 96]
    candel_tb = take_data_candle(asset, day_interval)  # Получаем набор свечей
    # Запускаем попытку поиска на YHOO
    print(candel_tb[:5])
    # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя

    if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
        candel_tb = dop_data.yhoo_data_taker(asset, day_interval)  # Попытка получить набор свечей с Yhoo
        print(candel_tb[:5])
        if len(candel_tb) < 30:
            return

    candel_tb['signal'] = 0
    for i in range(len(n1)):
        name_1 = str(n1[i])  # получаем имя для графика
        name_2 = str(n2[i])
        candel_tb['EWA1-' + name_1] = ema_f(candel_tb, n1[i])  # Эксопненциальная скользящая средняя №1
        candel_tb['EWA2-' + name_2] = ema_f(candel_tb, n2[i])  # Эксопненциальная скользящая средняя №2
        candel_tb['xk'] = candel_tb['EWA1-' + name_1] - candel_tb['EWA2-' + name_2]
        standert_dev_63 = candel_tb['Close'][-63::1].std()  # Стандартное отклонение 63 дня
        candel_tb['yk'] = candel_tb['xk'] / standert_dev_63
        standert_dev_252 = candel_tb['yk'][-252::1].std()  # Стандартное отклонение 252 дня
        candel_tb['zk'] = candel_tb['yk'] / standert_dev_252
        print('станд отклонеение', standert_dev_252)
        candel_tb['uk'] = (candel_tb['zk'] * (math.e ** (-(candel_tb['zk'] ** 2) / 4))) / (
                math.sqrt(2) * math.e ** (-1 / 2))  # Функция реакции
        wk = 1 / 3  # Веса
        candel_tb['signal'] += wk * candel_tb['uk']  # получения сигнала
        candel_tb['asset'] = asset
        print("[Ход выполнения", i)
    # print(candel_tb)

    candel_tb['signal'] = candel_tb['signal'].round(2)
    print(candel_tb[-2::1])

    global last_signal
    candel_tb['Удар'] = filter_signal(
        candel_tb[['asset', 'signal']][-2::1])  # Запускаем функцию рассматриваем только два дня
    print("============= \n", candel_tb[['asset', 'signal']][-1:])
    last_signal = pd.concat([last_signal, candel_tb[['asset', 'signal', 'Удар']][-1:]],
                            ignore_index=True)  # Таблица имя инструмента/сигнал для заполнения

    fig.add_trace(go.Scatter(x=candel_tb['Open time'], y=candel_tb['signal'], name=asset))  # Обновление для графиков
    fig.update_layout(title=asset, yaxis_title='singnal')
    return last_signal


def filter_signal(signal):
    """Фильтр по коэффициенту signal. Принимает название инструмента и таблицу сигналов """
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
    print('------------' * 10)
    print(table)
    fig = go.Figure(data=[go.Candlestick(x=table['Open time'],
                                         open=table['Open'],
                                         high=table['High'],
                                         low=table['Low'],
                                         close=table['Close']),
                          go.Scatter(x=table['Open time'], y=table['EWA1-8'], line=dict(color='red', width=1)),
                          go.Scatter(x=table['Open time'], y=table['EWA2-24'], line=dict(color='orange', width=1))])
    fig.update_layout(title=assetname, yaxis_title='price', paper_bgcolor='rgb(141,238,238)', linecolor='#636363')
    fig.show()
    time.sleep(5)


def chooise_find(day):
    """Выбор что найти хотим"""
    inp = input("выберите что ищем:  1- сигнал 2-график")
    if int(inp) == 1:
        table.apply(lambda x: fun_graf_delta(x.asset, day), axis=1)
    elif int(inp) == 2:
        table.apply(lambda x: fun_ewa(x.asset, day), axis=1)
    else:
        return chooise_find()


def balancer(last_signal):
    """Функция балансировки портфеля"""
    last_signal.reset_index(inplace=True, drop=True)

    print("Таблица требуемая 1 \n", last_signal)
    balance_portf = last_signal.query(
        '(asset != "BTC") & (asset != "DX-Y.NYB") & (asset != "GOLD") & (asset != "BZ=F") & (asset != "RUB=X")')  # Таблица чисто по портфелю без добавленных выше элементов
    balance_portf = balance_portf.reset_index(drop=True)
    print("Таблица требуемая \n", balance_portf)
    summa_tb_1 = balance_portf['signal'].sum()
    print("сумма", summa_tb_1)
    balance_portf["% balance"] = balance_portf['signal'] / summa_tb_1  # необходимое количество в процентах в портфеле.
    portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    volume_usdt = balance_mod.volume_usdt
    portf_table_current = portf_table_current.append({'asset': "USD", 'USDT': volume_usdt[0]},
                                                     ignore_index=True)  # Добавили строку с объемом текущих наличных долларов
    summa_portf_cost = portf_table_current['USDT'].sum()  # Сумма по таблице с текущим портфелем
    sred = portf_table_current['USDT'].mean()  # Среднее значение
    portf_table_current = portf_table_current.merge(balance_portf, how='left', on='asset')
    print("Текущий баланс \n", portf_table_current)

    portf_table_current[["Sharp_14", "Sortino_14"]] = portf_table_current["asset"].apply(
        lambda x: ssf.find_sharp_sortino(x, 14))  # Инициализация функции поиска

    if sred < 0.5:  # Страховка портфеля
        USD_new = summa_portf_cost * 0.4  # оставить 40% денег в кеше
        portf_table_current["USDT_new"] = summa_portf_cost * portf_table_current[
            "signal"] / summa_tb_1 - USD_new  # Значения которые должны быть на самом деле
        portf_table_current.loc[portf_table_current['asset'] == "USD", "USDT_new"] = USD_new

    else:
        portf_table_current["USDT_new"] = summa_portf_cost * portf_table_current[
            "signal"] / summa_tb_1  # Значения которые должны быть на самом деле
        portf_table_current.loc[portf_table_current['asset'] == "USD", "USDT_new"] = 0

    portf_table_current['by/cell'] = pow(portf_table_current['USDT_new'] - portf_table_current['USDT'],
                                         1)  # Количество долларов на которое надо продать или купить в портфель

    print("Необходимая действия \n", portf_table_current)
    a=input("повторить балансировку")
    return portf_table_current


if __name__ == '__main__':
    table = ask_input()
    # tableable = table[0:2]
    # ВНИМАНИЕ! строкой ниже Биток должен быть всегда первыми иначе фильтр работать не будет
    base_table = pd.DataFrame({'asset': ['BTC', 'DX-Y.NYB', "GOLD", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table = pd.concat([base_table, table], ignore_index=True)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    print('Таблица c позициями \n', table)
    day = 360  # Дни поиска
    chooise_find(day)  # Запуск выбора что таблиц поиска
    last_signal.dropna(how='all', inplace=True)
    last_signal.sort_values(by=['signal'], inplace=True)
    select_2 = last_signal.query('(Удар == "UP") | (Удар == "Down")')
    print('Таблица c найденными значениями  \n', select_2)
    fig.show()  # Отображение графикав

    insert_excel(select_2.reset_index(), "AF1")
    new_portf_balance = balancer(last_signal)  # Запуск балансера для портфеля
    print("Вставить данные по портфелю?")
    insert_excel(new_portf_balance, "Q1")
    select_1 = last_signal.query('signal > 0.5')
    insert_excel(select_1.reset_index(), "L1")


    transfer_data(last_signal)  # Данные для yhooo
    print('END')
    # table.apply(lambda x:take_data_candle(x.asset,10),axis=1)
