import pandas as pd
import balance_mod
import find_sharp_sortino as ssf
from datetime import date

def balancer(last_signal):
    """Функция балансировки портфеля"""
    portf_table_current = balance_mod.table  # Вызов текущей таблицы в портфеле
    volume_usdt = balance_mod.volume_usdt
    portf_table_current = portf_table_current.append({'asset': "USD", 'USDT': volume_usdt[0]},
                                                     ignore_index=True)  # Добавили строку с объемом текущих наличных долларов
    summa_portf_cost = portf_table_current['USDT'].sum()  # Сумма по таблице с текущим портфелем
    sred = portf_table_current['USDT'].mean()  # Среднее значение
    print(last_signal)
    print(portf_table_current)

    portf_table_current = portf_table_current.merge(last_signal, how='left', on='asset')
    summa_tb_1 = portf_table_current['signal'].sum()

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

    print("Необходимые действия \n", portf_table_current)
    a = input("повторить балансировку")
    if a=="1":
        return balancer(last_signal)
    return portf_table_current


def read_csv_():
    #Читаем файл с данными
    tcur_time=date.today()
    tcur_time=tcur_time.strftime("%m%d%Y")
    print("время",tcur_time)
    # table=table['asset']
    name="all_find_signal"

    last_signal_table = pd.read_csv(f'B:/download/{str(tcur_time)+name}.csv')
    last_signal_table=last_signal_table[['asset.1','signal']]
    last_signal_table.rename(columns={'asset.1':'asset'},inplace=True)
    last_signal_table.reset_index(inplace=True,drop=True)
    last_signal_table['asset']=last_signal_table['asset'].apply(lambda x: x.replace('/USD',''))
    return last_signal_table




if __name__=="__main__":
    last_signal_table=read_csv_()
    print("---\n" ,last_signal_table)

    balancer(last_signal_table)
