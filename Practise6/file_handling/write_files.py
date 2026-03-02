from pathlib import Path

def main() -> None:
    # Create a file and write sample data
    filename = Path("sample.txt")

    lines = [
        "Name: Alex\n",
        "City: Almaty\n",
        "Score: 95\n"
    ]

    filename.write_text("".join(lines), encoding="utf-8")
    print(f"[OK] Created and wrote: {filename.resolve()}")

    # Append new lines
    with filename.open("a", encoding="utf-8") as f:
        f.write("Status: Active\n")
        f.write("Note: Appended line\n")

    print("[OK] Appended new lines to sample.txt")


if __name__ == "__main__":
    main()