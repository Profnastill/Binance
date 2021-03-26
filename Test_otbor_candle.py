def __naznachalka(select, condition, name):
    if condition == True:
        print("да")
        print([select['ID'], select['type']])
        data = name
        return data, select['ID']
    else:
        print("нет")
        print(select['type'])
        return None # Ничего не возвращает если модель не найдена


def candles_model_analiz1(data):
    if __name__ == '__main__':
        test_tb = pd.DataFrame({'такури': ['б', 'б', 'б'], 'зонтик': ['к', 'к', 'к']}) #строка только для теста как модуля

    test_tb=pd.DataFrame({'Три солдата': ['Больш. бел. свеча', 'Больш. бел. свеча', 'Больш. бел. свеча'],
                          'Три вороны': ['Больш. крас. свеча', 'Больш. крас. свеча', 'Больш. крас. свеча'],
                          'Удар сокола': ['Больш. бел. свеча','"Мален. крас. свеча','Больш. крас. свеча']})
    x = len(data)

    for i in range(x // 3):
        select = data[x - 3:x:1]  # получаем срез
        print("--t" * 10)
        print(select)
        x -= 1
        print("-e-" * 10)
        print(list(test_tb.columns.values))

        for name in list(test_tb.columns.values):
            list_tb = test_tb[name].values
            list_select = select['type'].values
            print(list_tb)
            print(list_select)
            condition = str(list_tb) == str(list_select)
            data = __naznachalka(select, condition, name)
        return data

if __name__ == '__main__':
    import pandas as pd
    import random as rd

    massiv = []
    pd.options.display.max_rows = 1000
    for i in range(100):
        choise = rd.randint(0, 1)
        if choise == 0:
            choise = 'б'
        else:
            choise = 'к'
        massiv.append(choise)

    print(len(range(10, 110)))

    print(massiv)
    df = pd.DataFrame(
        {'ID': range(100), 'col_1': range(5, 105), 'col_2': range(8, 108), 'col_3': range(10, 110), 'type': massiv})
    print(df)

type = candles_model_analiz1(df)
print(type)

