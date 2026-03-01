import math

class Circle:
    def __init__(self, r):
        self.r = r

    def area(self):
        return math.pi * self.r * self.r

r = int(input())
c = Circle(r)
a = c.area()
print(f"{a:.2f}")
