import pandas as pd


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
    return fun1()

ren=fun1()
print (ge)