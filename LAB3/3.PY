words = {
    "ZER": "0", "ONE": "1", "TWO": "2", "THR": "3",
    "FOU": "4", "FIV": "5", "SIX": "6",
    "SEV": "7", "EIG": "8", "NIN": "9"
}

rev = {v: k for k, v in words.items()}

s = input().strip()

for op in ['+', '-', '*']:
    if op in s:
        left, right = s.split(op)
        break

def decode(x):
    res = ""
    for i in range(0, len(x), 3):
        res += words[x[i:i+3]]
    return int(res)

a = decode(left)
b = decode(right)

if op == '+':
    result = a + b
elif op == '-':
    result = a - b
else:
    result = a * b

ans = ""
for d in str(result):
    ans += rev[d]

print(ans)
