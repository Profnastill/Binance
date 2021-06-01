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


print("----")
df2 = pd.DataFrame({'ID': ['1', '2', '3', '4'], 'col_1': [7, 2, 7, 3], 'col_2': [1, 4, 5, 4], 'col_3': [3, 4, 6, 5]})
t=pd.DataFrame()
t=t.append((df2))
print(t)


class portf:
    def __init__(self,balance):
        self.__balans=balance
        self.__free=0
        self.price=1
        self.__comissia=0.1

    def __set_free(self,count):
        self.__free+=count
        self.__balans+=count*self.price-count*self.price*self.__comissia

    def __get_balance(self):
        return self.__balans

    def __get_free(self):
        print("Баланс текущий {self.__free}")
        return self.__free

    change_free=property(__get_free,__set_free)
    balance=property(__get_balance)

a=portf(10000)
a.change_free=-20
print(a.balance)
