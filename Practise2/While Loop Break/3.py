# Example 3: Break on user input
while True:
    command = input("Type 'exit' to stop: ")
    if command == "exit":
        break
    print("You typed:", command)
