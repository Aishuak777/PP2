# Example 4: Stop searching in a list
colors = ["red", "blue", "green", "yellow"]
i = 0
while i < len(colors):
    if colors[i] == "green":
        break
    print(colors[i])
    i += 1
