import binance2 as bs
import datetime
import pandas as pd
from binance.enums import *
import xlwings as xl
import keyboard


pd.options.display.max_rows=1000
pd.options.display.max_columns=10
pd.options.display.expand_frame_repr = False


table=bs.table# Текущий портфель
client=bs.client

interval = '1d'
# start_str=datetime.datetime(2021,1,1)
daily_interval=1

time_delta = datetime.timedelta(days=daily_interval)  # Интервал вычесления в днях
print(time_delta)
time_delta = time_delta.total_seconds()


start_str = time_delta


def orders_info(asset,time):
    '''
    Информация по ордерам
    {
        "symbol": "LTCBTC",
        "orderId": 1,
        "clientOrderId": "myOrder1",
        "price": "0.1",
        "origQty": "1.0",
        "executedQty": "0.0",
        "status": "NEW",
        "timeInForce": "GTC",
        "type": "LIMIT",
        "side": "BUY",
        "stopPrice": "0.0",
        "icebergQty": "0.0",
        "time": 1499827319559
    }
]'''
    print ("---",asset,time)
    orders_table=client.get_all_orders(symbol=asset+"USDT",recvWindow=int(6000) )
    orders_table=pd.DataFrame(orders_table)

    orders_table["time"]=orders_table["time"].apply(lambda x: datetime.datetime.fromtimestamp(int(x)/1000))
    orders_table=orders_table[["symbol","side","price","time"]]
    print(orders_table)


def funct_by_sell(order_type,data=table):
    ''' Функция продажи или покупки инструментов'''
    order = client.create_test_order(
    symbol='BNBUSDT',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.00001')



def funct_click():
    '''вызов действия'''
    click_type={1:"sell all",2:"by_all",3:"by",4:"sell"}
    print(click_type)
    try:
        a=int(input(f"выбор действия"))
    except:
        funct_click()

    if a==1:
        funct_by_sell("sell")
    elif a==2:
        funct_by_sell("by")
    elif a==3:
        funct_by_sell("by")
    elif a==4:
        funct_by_sell("sell")
    else: funct_click()

translate = {
    'down':' нажал на клавишу ',
    'up':' отпустил клавишу ',
    'o': 'нажал o'
}



def print_pressed_keys(e):
    print(
        'Пользователь {}{}'.format(translate[e.event_type], e.name)
        )

    if e.name=='o':
        a = table["asset"].apply(lambda x: orders_info(x, start_str))
    elif e.name=='enter':
        funct_click()



if __name__ == '__main__':
    #print(table["asset"] )

    keyboard.hook(print_pressed_keys)
    keyboard.wait()
