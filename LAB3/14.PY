import sys

n = int(sys.stdin.readline())
a = list(map(int, sys.stdin.readline().split()))
q = int(sys.stdin.readline())

for _ in range(q):
    parts = sys.stdin.readline().split()
    op = parts[0]

    if op == "add":
        x = int(parts[1])
        a = list(map(lambda v: v + x, a))
    elif op == "multiply":
        x = int(parts[1])
        a = list(map(lambda v: v * x, a))
    elif op == "power":
        x = int(parts[1])
        a = list(map(lambda v: v ** x, a))
    else:  # abs
        a = list(map(lambda v: abs(v), a))

print(*a)
