# Example 5: Break using a random number
import random

while True:
    n = random.randint(1, 10)
    print(n)
    if n == 7:
        print("Lucky number 7! Stop.")
        break
