"""Модуль проверки по сигналу на основе скользящего среднего, так же строим графики свечей"""
import math
# import stocker
import time
import pandas as pd
import plotly.graph_objects as go
# import dash
from find_sharp_sortino import take_data_candle, ask_input

'''''''''''
# from stocker import
stiker = stocker.predict.tomorrow('AAPL')

print(stiker)
'''''


def ema_f(table, n):
    """Функция экспоненциальной EMA нужна для ewa"""
    halflife = math.log(0.5) / math.log(1 - 1 / n)
    # ewm=pd.Series.ewm(table['Close'], alpha=n, halflife=halflife).mean()
    #ewm = pd.Series.ewm(table['Close'], alpha=1 / n).mean()
    ewm = pd.Series.ewm(table['Close'], halflife=halflife).mean()
    return pd.Series(ewm)


def fun_ewa(asset, day_interval):
    """Функция построения эксп скол средней."""
    n1 = [8, 16, 32]  # Коэффициент количество дней для сколь средней
    n2 = [24, 48, 96]
    candel_tb = take_data_candle(asset, day_interval)  # Получаем набор свечей
    # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
    for i in range(len(n1)):
        name_1=str(n1[i])
        name_2 = str(n2[i])
        candel_tb['EWA1-' + name_1] = ema_f(candel_tb, n1[i])  # Эксопненциальная скользящая средняя №1
        candel_tb['EWA2-' + name_2] = ema_f(candel_tb, n2[i])  # Эксопненциальная скользящая средняя №2
    grapf(candel_tb, asset)
    return candel_tb

fig=go.Figure() #Создаем график
def fun_ewa_delta(asset, day_interval):
    """Функция построения эксп скол средней."""
    n1 = [8, 16, 32]  # Коэффициент количество дней для сколь средней
    n2 = [24, 48, 96]
    candel_tb = take_data_candle(asset, day_interval)  # Получаем набор свечей
    # candel_tb['SMA1']= candel_tb.rolling(window=n1).mean()# Скользящая средняя
    candel_tb['signal']=0
    for i in range(len(n1)):
        print("---i",i)
        name_1=str(n1[i])#получаем имя для графика
        name_2 = str(n2[i])
        candel_tb['EWA1-' + name_1] = ema_f(candel_tb, n1[i])  # Эксопненциальная скользящая средняя №1
        candel_tb['EWA2-' + name_2] = ema_f(candel_tb, n2[i])  # Эксопненциальная скользящая средняя №2
        candel_tb['xk'] = candel_tb['EWA1-' + name_1] - candel_tb['EWA2-' + name_2]
        standert_dev_63 = candel_tb['Close'][-63::1].std()  # Стандартное отклонение
        candel_tb['yk'] = candel_tb['xk'] / standert_dev_63
        print ("стандартное отклонение",standert_dev_63)
        candel_tb['uk'] = (candel_tb['yk'] * (math.e ** (-(candel_tb['yk'] ** 2) / 4)))/(math.sqrt(2)*math.e**(-1/2))#Функция реакции
        wk = 1 / 3  # Веса
        candel_tb['signal'] += wk * candel_tb['uk']  # получения сигнала
        print ("-+"*10)
        print(candel_tb)
    fig.add_trace(go.Scatter(x=candel_tb['Open time'],y=candel_tb['signal'],name=asset))
    #fig=go.Figure(data=[go.Scatter(x=candel_tb['Open time'],y=candel_tb['signal'])])
    fig.update_layout(title=asset, yaxis_title='singnal')
    #fig.show()
    time.sleep(2)
    #input_enter()#Запуск запроса на продолжение работы программы
    #grapf(candel_tb, asset)
    return candel_tb

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

def chooise_find():
    inp=input("выберите что ищем:  1- сигнал 2-график")
    if int(inp)==1:
        table.apply(lambda x: fun_ewa_delta(x.asset, 240), axis=1)
    elif int(inp)==2:
        table.apply(lambda x: fun_ewa(x.asset, 240), axis=1)
    else:
        return chooise_find()


if __name__ == '__main__':
    table = ask_input()
    #table=table[0:2]
    chooise_find()# Запуск выбора что таблиц поиска
    fig.show()#Отображение графикав
    print('END')
    # table.apply(lambda x:take_data_candle(x.asset,10),axis=1)
