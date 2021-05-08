'''модуль графического анализа '''
import binance2 as bs
import datetime
import pandas as pd
from binance.enums import *
import xlwings as xl
import keyboard
import xlwings as xw
from binance.websockets import BinanceSocketManager



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

balance=client.get_account()['balances']
#print(balance)
table=pd.DataFrame(balance)
table['free']=table['free'].apply(lambda x: float(x))
selection_usdt = ((table.asset == "USDT"))
volume_usdt = table[selection_usdt]['free'].values#количество своободных средств
print(volume_usdt)





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


def funct_by_sell(data):
    ''' Функция продажи или покупки инструментов'''
    print("Запуски")
    print(data)
    print(data['curent_price']['price'])
    order = client.create_test_order(
    symbol=data['asset']+'USDT',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=0.1,
    price=str(data['curent_price']['price']))
    print (order)



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



def read_action_file():
    xlbook = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
    sheet = xlbook.sheets('Портфель')
    bs.table_base = sheet.range('A1').options(pd.DataFrame, expand='table', index=False).value
    return bs.table_base

def test_f(x):
    r=x+str(1)
    return r



if __name__ == '__main__':
    #print(table["asset"] )
    action_table=read_action_file()# читаем файл действий
    print(action_table)
    action_table['curent_price']=action_table['asset'].apply(lambda x: client.get_avg_price(symbol=(x+'USDT')))
    print(action_table.asset)
    action_table.apply(funct_by_sell,axis=1)
    #action_table.apply(lambda x: funct_by_sell(x.Action,"ooa"),axis=1)




    #keyboard.hook(print_pressed_keys)
    #keyboard.wait()
