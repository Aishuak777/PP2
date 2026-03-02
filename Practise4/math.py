import math

# 1) Convert degree to radian
deg = float(input("Input degree: "))
rad = deg * math.pi / 180
print("Output radian:", round(rad, 6))


# 2) Area of a trapezoid
h = float(input("Height: "))
b1 = float(input("Base, first value: "))
b2 = float(input("Base, second value: "))

trap_area = (b1 + b2) * h / 2
print("Expected Output:", trap_area)


# 3) Area of a regular polygon
sides = int(input("Input number of sides: "))
side_len = float(input("Input the length of a side: "))

poly_area = (sides * (side_len ** 2)) / (4 * math.tan(math.pi / sides))
print("The area of the polygon is:", round(poly_area, 0))


# 4) Area of a parallelogram
base_len = float(input("Length of base: "))
para_h = float(input("Height of parallelogram: "))

para_area = base_len * para_h
print("Expected Output:", para_area)