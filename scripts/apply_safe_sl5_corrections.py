"""Apply safe yellow-box coord corrections to sl5-hotspots.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
CORRECTIONS_PATH = ROOT / "private/sl5-coord-correction-table.json"

SAFE_ZONES = {
    "06", "07", "09", "13", "14",
    "17", "18", "19", "20", "21",
    "23", "24", "25", "26", "27", "28", "29", "30",
}


def main() -> None:
    zones = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    corrections = json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8"))
    by_zone = {c["zone"]: c["recommended"] for c in corrections}

    updated = 0
    for z in zones:
        zid = z.get("zone")
        if zid not in SAFE_ZONES or zid not in by_zone:
            continue
        rec = by_zone[zid]
        z["x"], z["y"], z["w"], z["h"] = rec["x"], rec["y"], rec["w"], rec["h"]
        updated += 1
        print(f"zone {zid} {z['title']}: -> x={rec['x']} y={rec['y']} w={rec['w']} h={rec['h']}")

    zones.sort(key=lambda item: str(item.get("zone", "")).zfill(2))
    JSON_PATH.write_text(json.dumps(zones, indent=2) + "\n", encoding="utf-8")
    print(f"\nUpdated {updated} zones in {JSON_PATH.name}")


if __name__ == "__main__":
    main()
