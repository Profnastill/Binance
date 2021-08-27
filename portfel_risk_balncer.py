"""Модуль балансировки порфеля по сигналу
Чтение происходит их предварительно записаной базы данных
"""

from datetime import date

import pandas as pd

import balance_mod
from candle_graf import insert_excel


def f_balancer(last_signal):
    """Функция балансировки портфеля"""
    portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    volume_usdt = balance_mod.volume_usdt
    portf_table_current = portf_table_current.append({'asset': "USD", 'USDT': volume_usdt[0]},
                                                     ignore_index=True)  # Добавили строку с объемом текущих наличных долларов

    print(last_signal)

    portf_table_current = portf_table_current.merge(last_signal, how='left', on='asset')
    summa_portf_cost = portf_table_current['USDT'].sum()  # Сумма по таблице с текущим портфелем
    print("теукщая табл \n", portf_table_current)
    sred = portf_table_current['signal'].mean(skipna=True)  # Среднее значение

    portf_table_current.loc[portf_table_current["signal"] < 0, ('signal')] = 0
    sum_signal = 1 / portf_table_current["signal"].sum()
    print(sum_signal)
    portf_table_current['необх колич $'] = summa_portf_cost * portf_table_current['signal'] * sum_signal
    portf_table_current["by/sell"] = (portf_table_current['необх колич $'] - portf_table_current['USDT'])

    summa_tb_1 = portf_table_current['signal'].sum()
    print("Текущий баланс \n", portf_table_current)

    if sred < -1:  # Страховка портфеля
        USD_new = portf_table_current["USDT"] * 0.4  # оставить 40% денег в кеше
        portf_table_current["USDT_new"] = summa_portf_cost * portf_table_current[
            "signal"] / summa_tb_1 - USD_new  # Значения которые должны быть на самом деле
        portf_table_current.loc[portf_table_current["asset"] == "USD", "USDT_new"] = USD_new.sum()


    else:
        portf_table_current["USDT_new"] = summa_portf_cost * portf_table_current[
            "signal"] / summa_tb_1  # Значения которые должны быть на самом деле
        portf_table_current.loc[portf_table_current['asset'] == "USD", "USDT_new"] = 0

    print(" Баланс новый\n", portf_table_current)
    return portf_table_current


"""""""""
    a = input("повторить балансировку input 1 ")
    if a=="1":
        return balancer(last_signal)
"""""""""""


def read_csv_():
    """читаем базу с данным
    и возвращаем сигнал"""
    tcur_time = date.today()
    tcur_time = tcur_time.strftime("%m%d%Y")
    print("время", tcur_time)
    # table=table['asset']
    name = "all_find_signal"

    last_signal_table = pd.read_csv(f'B:/download/{str(tcur_time) + name}.csv')
    last_signal_table = last_signal_table[['asset.1', 'signal', 'sharp', 'sortino']]
    last_signal_table.rename(columns={'asset.1': 'asset'}, inplace=True)
    last_signal_table.reset_index(inplace=True, drop=True)
    last_signal_table['asset'] = last_signal_table['asset'].apply(lambda x: x.replace('/USD', ''))
    return last_signal_table


def main():
    last_signal_table = read_csv_()  # читаем базу данных
    balance_tb = f_balancer(last_signal_table)
    return balance_tb


if __name__ == "__main__":
    balance_tb = main()
    print("Сумма по портфелю", balance_tb["USDT_new"].sum().round(0))
    insert_excel(balance_tb, 'j1', table_name="Портфель")
    # test_module()
