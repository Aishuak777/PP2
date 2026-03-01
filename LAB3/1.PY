n = input().strip()

is_valid = True
for ch in n:
    if int(ch) % 2 != 0:
        is_valid = False
        break

print("Valid" if is_valid else "Not valid")
