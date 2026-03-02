import json
from pathlib import Path

# Build path to JSON next to this script
base_dir = Path(__file__).resolve().parent
json_file = base_dir / "sample-data.json"

with json_file.open("r", encoding="utf-8") as f:
    payload = json.load(f)

print("\nInterface Status")
print("=" * 80)
print("{:<50} {:<20} {:<8} {:<6}".format("DN", "Description", "Speed", "MTU"))
print("-" * 80)

for obj in payload.get("imdata", []):
    attrs = obj.get("l1PhysIf", {}).get("attributes", {})

    dn = attrs.get("dn", "")
    descr = attrs.get("descr", "")
    speed = attrs.get("speed", "")
    mtu = attrs.get("mtu", "")

    print("{:<50} {:<20} {:<8} {:<6}".format(dn, descr, speed, mtu))