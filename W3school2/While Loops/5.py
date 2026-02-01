# Example 5: Loop until user types 'stop'
user_input = ""
while user_input.lower() != "stop":
    user_input = input("Type 'stop' to end: ")
    print("You typed:", user_input)
