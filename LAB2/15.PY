n = int(input())
surnames = set()

for _ in range(n):
    surnames.add(input().strip())

print(len(surnames))
