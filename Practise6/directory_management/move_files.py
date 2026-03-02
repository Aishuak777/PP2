import shutil
from pathlib import Path

def main() -> None:
    base = Path("workspace")
    src = base / "data" / "raw" / "b.txt"
    dest_dir = base / "data" / "processed"
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print("[WARN] workspace/data/raw/b.txt not found. Run create_list_dirs.py first.")
        return

    # Copy file
    copied_path = dest_dir / src.name
    shutil.copy2(src, copied_path)
    print(f"[OK] Copied: {src} -> {copied_path}")

    # Move file (rename)
    moved_path = dest_dir / "b_moved.txt"
    src.rename(moved_path)
    print(f"[OK] Moved: {src} -> {moved_path}")


if __name__ == "__main__":
    main()