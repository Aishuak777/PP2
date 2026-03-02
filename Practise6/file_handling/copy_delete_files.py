import shutil
from pathlib import Path

def safe_delete(file_path: Path) -> bool:
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return True
    return False

def main() -> None:
    src = Path("sample.txt")
    backup = Path("sample_backup.txt")

    if not src.exists():
        print("[WARN] sample.txt not found. Run write_files.py first.")
        return

    # Copy / backup using shutil
    shutil.copy2(src, backup)
    print(f"[OK] Backed up: {src} -> {backup}")

    # Delete files safely
    deleted = safe_delete(backup)
    print(f"[OK] Deleted {backup}? {deleted}")

    deleted_missing = safe_delete(Path("does_not_exist.txt"))
    print(f"[OK] Deleted does_not_exist.txt? {deleted_missing}")


if __name__ == "__main__":
    main()