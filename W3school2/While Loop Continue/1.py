# Example 1: Skip even numbers
i = 0
while i < 5:
    i += 1
    if i % 2 == 0:
        continue
    print(i)  # Prints only odd numbers: 1, 3, 5
