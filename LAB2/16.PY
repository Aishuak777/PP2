n = int(input())
a = list(map(int, input().split()))

seen = set()
for x in a:
    if x in seen:
        print("NO")
    else:
        print("YES")
        seen.add(x)
