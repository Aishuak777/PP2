from functools import reduce

def main() -> None:
    nums = [1, 2, 3, 4, 5, 6]

    # map(): transform each item
    squared = list(map(lambda x: x * x, nums))

    # filter(): keep items that match condition
    evens = list(filter(lambda x: x % 2 == 0, nums))

    # reduce(): aggregate into one value
    product = reduce(lambda acc, x: acc * x, nums, 1)

    print("nums:", nums)
    print("squared (map):", squared)
    print("evens (filter):", evens)
    print("product (reduce):", product)


if __name__ == "__main__":
    main()