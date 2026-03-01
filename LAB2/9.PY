n = int(input())
a = list(map(int, input().split()))

mn = a[0]
mx = a[0]

for x in a:
    if x < mn:
        mn = x
    if x > mx:
        mx = x

for i in range(n):
    if a[i] == mx:
        a[i] = mn

for x in a:
    print(x, end=" ")
