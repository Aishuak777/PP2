nums = list(map(int, input().split()))

def is_prime(x):
    if x < 2:
        return False
    d = 2
    while d * d <= x:
        if x % d == 0:
            return False
        d += 1
    return True

primes = list(filter(lambda x: is_prime(x), nums))

if primes:
    print(*primes)
else:
    print("No primes")
