from pathlib import Path

def main() -> None:
    filename = Path("sample.txt")

    if not filename.exists():
        print("[WARN] sample.txt not found. Run write_files.py first.")
        return

    content = filename.read_text(encoding="utf-8")
    print("[OK] File content:\n")
    print(content)


if __name__ == "__main__":
    main()