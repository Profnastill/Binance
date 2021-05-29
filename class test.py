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


a=5+49+9
print(a)