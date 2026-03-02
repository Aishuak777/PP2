# 1) Generator: squares from 0 to N
def gen_squares(limit):
    for x in range(limit + 1):
        yield x ** 2

for v in gen_squares(5):
    print(v)


# 2) Generator: even numbers 0..n, comma-separated
def gen_evens(limit):
    for x in range(0, limit + 1, 2):
        yield x

n = int(input("Enter a number: "))
print(",".join(map(str, gen_evens(n))))


# 3) Generator: numbers divisible by 3 and 4 from 0..n
def gen_div_3_and_4(limit):
    for x in range(limit + 1):
        if x % 12 == 0:          # same as divisible by 3 and 4
            yield x

for num in gen_div_3_and_4(50):
    print(num)


# 4) Generator: squares from a to b
def squares_range(a, b):
    for x in range(a, b + 1):
        yield x * x

for val in squares_range(3, 7):
    print(val)


# 5) Generator: countdown from n to 0
def gen_countdown(start):
    for x in range(start, -1, -1):
        yield x

for number in gen_countdown(5):
    print(number)