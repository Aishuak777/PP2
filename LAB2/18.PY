n = int(input())
first_pos = {}

for i in range(1, n + 1):
    s = input().strip()
    if s not in first_pos:
        first_pos[s] = i

for s in sorted(first_pos.keys()):
    print(s, first_pos[s])
