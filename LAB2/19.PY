n = int(input())
mp = {}

for _ in range(n):
    s, k = input().split()
    k = int(k)
    mp[s] = mp.get(s, 0) + k

for s in sorted(mp.keys()):
    print(s, mp[s])
