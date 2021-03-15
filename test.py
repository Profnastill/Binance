import pandas as pd

df = pd.DataFrame({'ID':['1', '2', '3'], 'col_1': [0, 2, 3], 'col_2':[1, 4, 5]})
mylist = ['a', 'b', 'c', 'd', 'e', 'f']

print (df)
def get_sublist(sta,end):
    return mylist[sta:end+1]



#df[["col_1","col_2"]]=df[["col_1","col_2"]].apply(lambda x: float(), axis=1)
#df[["col_1","col_2"]]=df[["col_1","col_2"]].apply(float(), axis=1)
df[["col_1","col_2"]]=df[["col_1","col_2"]].applymap(lambda x: float(x))

max=list(df[["col_1","col_2"]].max())

print(max)

#print(df)


print (abs(-4))