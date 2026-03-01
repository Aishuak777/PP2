n = int(input())
numbers = list(map(int, input().split()))

count = 0
for x in numbers:
    if x > 0:
        count += 1

print(count)
