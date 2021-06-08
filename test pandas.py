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


class portf_cls:
    def __init__(self,balance):
        self.__balans=balance
        self.__free=0
        self.price=1
        self.__comissia=0.1

    def __set_free(self,count):
        self.__free+=count
        self.__balans+=count*self.price-count*self.price*self.__comissia

    def __get_balance(self):
        print(f"Баланс текущий {self.__balans}")
        return self.__balans

    def __get_free(self):
        print(f"Баланс текущий {self.__free}")
        return self.__free

    change_free=property(__get_free,__set_free)
    balance=property(__get_balance)


class new:
    def __init__(self):
        self.b=self.change()
    def change(self):
        portf=portf_cls(10000)
        portf.change_free = -1111
        print(portf.balance)
        portf.balance


def sfds():
    gf=new()


sfds()

class sums:
    def __init__(self):
        self.sum=0
    def add(self,a):
        self.sum+=a



sums=sums()


class test:
    def __init__(self,a):
        self.a=a
        sums.add(a)

    @classmethod
    def summ(cls):
        return sums.sum

for i in [1,3,5]:
    start=test(i)
    start.summ()
print(start.summ())