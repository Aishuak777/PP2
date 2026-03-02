from pathlib import Path

def main() -> None:
    # Create nested directories
    nested = Path("workspace") / "data" / "raw"
    nested.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created nested dirs: {nested}")

    # Create some files for testing
    (nested / "a.csv").write_text("id,val\n1,10\n", encoding="utf-8")
    (nested / "b.txt").write_text("hello\n", encoding="utf-8")
    (nested / "c.csv").write_text("id,val\n2,20\n", encoding="utf-8")
    print("[OK] Created example files in workspace/data/raw")

    # List files and folders in workspace
    base = Path("workspace")
    print("\n[LIST] workspace contents:")
    for item in base.iterdir():
        kind = "DIR " if item.is_dir() else "FILE"
        print(kind, item.name)

    # Find files by extension
    csv_files = list(base.rglob("*.csv"))
    print("\n[FIND] CSV files found:")
    for f in csv_files:
        print("-", f)


if __name__ == "__main__":
    main()