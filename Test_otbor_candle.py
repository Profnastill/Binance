import pandas as pd
import random as rd


def candles_model_analiz(data):
    if __name__ == '__main__':
        test_tb = pd.DataFrame(
            {'такури': ['б', 'б', 'б'], 'зонтик': ['к', 'к', 'к']})  # строка только для теста как модуля
    else:
        test_tb = pd.DataFrame({'Три солдата': ['Б. бел.', 'Б. бел.', 'Б. бел.'],
                                'Три вороны': ['Б. крас.', 'Б. крас.', 'Б. крас.'],
                                'Удар сокола': ['Б. бел.', '"М. крас.', 'Б. крас.'],
                                'Две черные вороны':['Б. бел. свеча','М. крас. свеча','Б. крас.'],
                                'Черные в ряд':['Б. бел.','Б. крас.','Б. крас.'],
                                'Черные в ряд_2': ['Б. бел. свеча','Б. крас.', 'М. крас.'],
                                'Белые в ряд':['Б. крас.','Б. бел.','Б. бел.'],
                                'Белые в ряд_2':['Б. крас.','М. бел.','М. бел.']})
    x = len(data)
    ls = []

    for name in list(test_tb.columns.values):  # name-это название модели

        list_tb = (test_tb[name].values)  # Получаем модели возможных комбинаций свечей
        n_lenght = len(list_tb)
        for i in range(x // n_lenght):  # Перебираем модели
            select = data[x - 3:x:1]  # получаем срез из набора свечей
            print("--t" * 10)
            print(select)
            x -= 1
            print(list(test_tb.columns.values))
            list_select = (select['type'].values)
            condition = str(list_tb) == str(list_select)
            if condition == True:
                print("да")
                name  # name-это название модели
                print(select)
                print(select['Open time'][0:1])

                ls.append([(select['Open time'][0:1].values), name])

            else:

                print("нет")
                print(select['type'])
                continue
                # Ничего не возвращает если модель не найдена
                # ls.append(select['Open time'])
        # print("ls", ls)

    print("результат поиска модели", ls)
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
        {'Open time': range(100), 'col_1': range(5, 105), 'col_2': range(8, 108), 'col_3': range(10, 110),
         'type': massiv})
    print(data)

    type = candles_model_analiz(data)
    print(type)
