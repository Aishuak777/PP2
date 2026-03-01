n, l, r = map(int, input().split())
a = list(map(int, input().split()))

l -= 1
r -= 1

i, j = l, r
while i < j:
    a[i], a[j] = a[j], a[i]
    i += 1
    j -= 1

for x in a:
    print(x, end=" ")
