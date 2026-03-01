class StringHandler:
    def getString(self):
        self.s = input()

    def printString(self):
        print(self.s.upper())

obj = StringHandler()
obj.getString()
obj.printString()
