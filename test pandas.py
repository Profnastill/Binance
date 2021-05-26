import pandas as pd
from datetime import date
import pprint,os


df = pd.DataFrame({'ID':['1', '2', '3','4'], 'col_1': [7, 2, 7,3], 'col_2':[1, 4, 5,4],'col_3':[3,4,6,5]})
print(df)

print(df.iloc[[0]])




def  fun1():
    fun2(1)

def fun2 (x):
    global ge
    ge=pd.DataFrame()
    df2 = pd.DataFrame({'ID': ['1', '2', '3', '4'], 'col_1': [7, 2, 7, 3], 'col_2': [1, 4, 5, 4], 'col_3': [3, 4, 6, 5]})

    ge=pd.concat([df,ge],ignore_index=True)
    return ge


ren=fun2(1)
print("-"*10)
print (ge)

print (ge[-1::])