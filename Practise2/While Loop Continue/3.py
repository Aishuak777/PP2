# Example 3: Skip empty input
while True:
    text = input("Enter something (or 'stop' to end): ")
    if text == "":
        continue  # Skip empty input
    if text.lower() == "stop":
        break
    print("You entered:", text)
