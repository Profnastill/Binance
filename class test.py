from itertools import *
class test:
    def __init__(self, name):
        self.name = name
        self.p="+aas"

    def chager2(self):
        self.name += "_ada"

    def chager(self):
        self.name += "_ada"+self.p



a = test("addssa")
a.p="привет"
a.chager()
print(a.name)


def znach_find():
    """Нахождение возможных значений весов"""
    a = []
    _list=[0.15,0.2, 0.25, 0.35, 0.40, 0.45, 0.5, 0.55, 0.6,0.8]
    #_list = [0.2, 0.25, 0.35]
    for i in permutations(_list, 3):
        if sum(i) == 1:
            a.append(i)
    print(a)
    print(len(a))
    return a


a=znach_find()