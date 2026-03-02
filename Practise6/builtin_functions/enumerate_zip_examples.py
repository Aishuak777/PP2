def main() -> None:
    names = ["Ali", "Dana", "Mira"]
    scores = [88, 95, 72]

    print("Enumerate (index + value):")
    for i, name in enumerate(names, start=1):
        print(i, name)

    print("\nZip (pair iteration):")
    for name, score in zip(names, scores):
        print(f"{name} -> {score}")

    print("\nType checking + conversions:")
    values = ["10", "3.14", 7, True, None]

    for v in values:
        print("value:", v, "| type:", type(v))

    a = int("10")
    b = float("3.14")
    c = str(123)
    d = bool(0)
    e = list("abc")

    print("\nConverted:")
    print(a, type(a))
    print(b, type(b))
    print(c, type(c))
    print(d, type(d))
    print(e, type(e))


if __name__ == "__main__":
    main()