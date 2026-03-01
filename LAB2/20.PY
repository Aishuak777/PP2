q = int(input())
db = {}

for _ in range(q):
    parts = input().split()
    if parts[0] == "set":
        key = parts[1]
        value = parts[2]
        db[key] = value
    else:  # get
        key = parts[1]
        if key in db:
            print(db[key])
        else:
            print(f"KE: no key {key} found in the document")
