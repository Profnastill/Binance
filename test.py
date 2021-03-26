import pandas as pd

df = pd.DataFrame({'ID':['1', '2', '3'], 'col_1': [7, 2, 7], 'col_2':[1, 4, 5],'col_3':[8,4,6]})
mylist = ['a', 'b', 'c', 'd', 'e', 'f']

print (df)
def get_sublist(sta,end):
    return mylist[sta:end+1]



#df[["col_1","col_2"]]=df[["col_1","col_2"]].apply(lambda x: float(), axis=1)
#df[["col_1","col_2"]]=df[["col_1","col_2"]].apply(float(), axis=1)
df=df[["col_1","col_2","col_3"]].applymap(lambda x: float(x))

#df["max"]=max(df['col_1'],df['col_2'])
max=list(df[["col_1","col_2"]].max())

raznost=abs(df['col_1']-df['col_2'])
print("raz\n",raznost)

col1=df['col_1']
col2=df['col_2']
col3=df['col_3']

sravn=(col1>col2)
print ('t1',sravn)
sravn=(col1>col3)
print ('t2',sravn)

print ('****-'*10)
sravn=[(col1>col2) & (col1>col3)]




print (sravn)
sravn= (col1>col3) | (col1>col2)
print (sravn)






def funct2(table):
    print ("---",table.col_1,table.col_2,table.col_3)
    print ((table.col_1>table.col_2) | (table.col_1>table.col_3))
    if ((table.col_1>table.col_2) | (table.col_1>table.col_3))==True:
        val='Yes'
    else:
        val = 'None'
    return val


df['type']=df.apply(funct2,axis=1)
print ('-x-x-x'*3)
print (df)



open=120
close=121
topshadow=3
bottomshadow=0.1


a=open%close
print("a",a)

list=[-1,0,1]
print (range(len(list)))

if (abs(open/close)):
    None
list=[1,2,3,4,5,6,7,9,10,11]
print(list[-3::1])