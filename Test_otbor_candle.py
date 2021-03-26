import pandas as pd
import random as rd

def __naznachalka(select, condition, name):
    if condition == True:
        print("да")
        print([select['Open time'], select['type']])
        data = name #name-это название модели
        return select['Open time'], name
    else:
        print("нет")
        print(select['type'])
        # Ничего не возвращает если модель не найдена
        return select['Open time']


def candles_model_analiz(data):
    if __name__ == '__main__':
        test_tb = pd.DataFrame({'такури': ['б', 'б', 'б'], 'зонтик': ['к', 'к', 'к']}) #строка только для теста как модуля
    else:
        test_tb=pd.DataFrame({'Три солдата': ['Больш. бел. свеча', 'Больш. бел. свеча', 'Больш. бел. свеча'],
                              'Три вороны': ['Больш. крас. свеча', 'Больш. крас. свеча', 'Больш. крас. свеча'],
                              'Удар сокола': ['Больш. бел. свеча','"Мален. крас. свеча','Больш. крас. свеча']})

    x = len(data)
    print (x)
    ls=[]

    print('-ggg1-' * 10)
    print(data)
    for name in range(x // 3):
        select = data[x - 3:x:1]  # получаем срез из набора свечей
        print("--t" * 10)
        print(select)
        x -= 1
        print(list(test_tb.columns.values))
        for name in list(test_tb.columns.values):# Перебираем модели
            list_tb = (test_tb[name].values)
            list_select = (select['type'].values)
            condition = str(list_tb) == str(list_select)
            print("-/-"*3)
            print ((list_tb))
            print (str(list_select))
            print("-/-" * 3)
            #find_ = __naznachalka(select, condition, name)# Это функция какой то бред так как пустая по сути
            if condition == True:
                print("да")
                name  # name-это название модели
                print (select)
                print (select['Open time'][0:1])

                ls.append([(select['Open time'][0:1].values), name])

            else:
                print("нет")
                print(select['type'])
                # Ничего не возвращает если модель не найдена
                #ls.append(select['Open time'])
           # print("ls", ls)


    print ("результат поиска модели",ls)
    return ls

if __name__ == '__main__':

    massiv = []
    pd.options.display.max_rows = 1000
    for i in range(100):
        choise = rd.randint(0, 1)
        if choise == 0:
            choise = 'б'
        else:
            choise = 'к'
        massiv.append(choise)

    print(massiv)
    data = pd.DataFrame(
        {'Open time': range(100), 'col_1': range(5, 105), 'col_2': range(8, 108), 'col_3': range(10, 110), 'type': massiv})
    print(data)

    type = candles_model_analiz(data)
    print(type)

