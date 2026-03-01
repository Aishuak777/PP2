n = int(input())
cnt = {}

for _ in range(n):
    s = input().strip()
    cnt[s] = cnt.get(s, 0) + 1

ans = 0
for v in cnt.values():
    if v == 3:
        ans += 1

print(ans)
