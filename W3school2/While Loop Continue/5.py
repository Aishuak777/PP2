# Example 5: Skip certain letters
word = "python"
i = 0
while i < len(word):
    i += 1
    if word[i-1] in "aeiou":
        continue
    print(word[i-1])  # Skips vowels: p, t, h, n
