n = int(input())

if n <= 0:
    print("NO")
else:
    p = 1
    while p < n:
        p *= 2
    print("YES" if p == n else "NO")
