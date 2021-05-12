"""Модуль проверки по сигналу на основе скользящего среднего, так же строим графики свечей"""
import math
# import stocker
import time

import pandas as pd
import plotly.graph_objects as go

import balance_mod
import dop_data
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
last_signal = pd.DataFrame(columns=columns)  # Пустая таблица для добавления в нее данных


# print(last_signal)


def fun_ewa_delta(asset, day_interval):
    """Функция построения эксп скол средней."""
    n1 = [8, 16, 32]  # Коэффициент количество дней для сколь средней
    n2 = [24, 48, 96]
    candel_tb = take_data_candle(asset, day_interval)  # Получаем набор свечей
    # Запускаем попытку поиска на YHOO
    print(candel_tb[:5])
    # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя

    if len(candel_tb) < 26:  # Защита если таблица вдруг пустая пришла
        candel_tb = dop_data.yhoo_data_taker(asset, day_interval)  # Попытка получить набор свечей с Yhoo
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
    global last_signal
    last_signal = pd.concat([last_signal, candel_tb[['asset', 'signal']][-1:]], ignore_index=True)
    fig.add_trace(go.Scatter(x=candel_tb['Open time'], y=candel_tb['signal'], name=asset))
    fig.update_layout(title=asset, yaxis_title='singnal')

    return last_signal


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
    fig.update_layout(title=assetname, yaxis_title='price')
    fig.show()
    time.sleep(5)


def chooise_find(day):
    """Выбор что найти хотим"""
    inp = input("выберите что ищем:  1- сигнал 2-график")
    if int(inp) == 1:
        table.apply(lambda x: fun_ewa_delta(x.asset, day), axis=1)
    elif int(inp) == 2:
        table.apply(lambda x: fun_ewa(x.asset, day), axis=1)
    else:
        return chooise_find()


def balancer(last_signal):
    """Функция балансировки портфеля"""
    last_signal.reset_index(inplace=True, drop=True)
    # last_signal['signal']=last_signal.query('signal<0.4')

    print("Таблица требуемая 1 \n", last_signal)
    balance_portf = last_signal.query(
        '(asset != "BTC") & (asset != "DX-Y.NYB") & (asset != "GOLD") & (asset != "BZ=F") & (asset != "RUB=X")')  # Таблица чисто по портфелю без добавленных выше элементов
    # balance_portf = last_uk.query('asset != "BTC"')
    balance_portf = balance_portf.reset_index(drop=True)
    print("Таблица требуемая \n", balance_portf)
    summa_tb_1 = balance_portf['signal'].sum()
    print("сумма", summa_tb_1)
    balance_portf["% balance"] = balance_portf['signal'] / summa_tb_1  # необходимое количество в процентах в портфеле.

    portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    summa_tb_2 = portf_table_current['USDT'].sum()  # Сумма по таблице с текущим портфелем
    portf_table_current = portf_table_current.merge(balance_portf, how='left', on='asset')
    print("Текущий баланс \n", portf_table_current)
    # portf_table_current['free'] = portf_table_current['free'].apply(float)
    portf_table_current["USDT_new"] = summa_tb_2 * portf_table_current[
        "signal"] / summa_tb_1  # Значения которые должны быть на самом деле

    portf_table_current['by/cell'] = pow(portf_table_current['USDT_new'] - portf_table_current['USDT'],
                                         1)  # Количество долларов на которое надо продать или купить в портфель

    print("Необходимая действия \n", portf_table_current)
    return portf_table_current


if __name__ == '__main__':
    table = ask_input()
    # table = table[0:4]
    # base_table=pd.DataFrame({'asset':['BTC','EOS','BNB']})
    base_table = pd.DataFrame({'asset': ['BTC', 'DX-Y.NYB', "GOLD", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table = pd.concat([table, base_table], ignore_index=True)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    print('Таблица c позициями \n', table)
    day = 360  # Дни поиска
    chooise_find(day)  # Запуск выбора что таблиц поиска

    last_signal.sort_values(by=['signal'], inplace=True)
    # print('\n Таблица с коэффициентами \n', last_uk.reset_index(inplace=True,drop=True))
    new_portf_balance = balancer(last_signal)  # Запуск балансера для портфеля
    insert_excel(new_portf_balance, "Q1")
    last_signal = last_signal.query('signal > 0.5')

    insert_excel(last_signal.reset_index(), "L1")  # Только двадцать лучших
    fig.show()  # Отображение графикав
    transfer_data(last_signal)  # Данные для yhooo
    print('END')
    # table.apply(lambda x:take_data_candle(x.asset,10),axis=1)
