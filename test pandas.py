import pandas as pd
from datetime import date
import pprint,os

pprint.pprint(os.path.abspath(binance.__file__))

df = pd.DataFrame({'ID':['1', '2', '3','4'], 'col_1': [7, 2, 7,3], 'col_2':[1, 4, 5,4],'col_3':[3,4,6,5]})
print(df)

print(df.iloc[[0]])

def  fun1():
    fun2(1)

def fun2 (x):
    df2 = pd.DataFrame({'ID': ['1', '2', '3', '4'], 'col_1': [7, 2, 7, 3], 'col_2': [1, 4, 5, 4], 'col_3': [3, 4, 6, 5]})
    global ge
    ge=pd.concat([df,df2],ignore_index=True)
    print(df.iloc[[2]])
    print(ge)
    return ge


ren=fun1()
print (ge)

def insert_csv(table,name):

    """Сохдание файла базы"""
    table.to_csv(f'B:/download/da.csv',index_label= 'asset')
    return

insert_csv(ge,"name")

tcur_time = date.today()
tcur_time = tcur_time.strftime("%b_%d_%Y")
print (tcur_time)
print(tcur_time is str)