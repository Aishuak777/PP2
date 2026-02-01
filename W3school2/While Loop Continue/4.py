# Example 4: Skip numbers divisible by 3
i = 0
while i < 10:
    i += 1
    if i % 3 == 0:
        continue
    print(i)  # Skips 3, 6, 9
