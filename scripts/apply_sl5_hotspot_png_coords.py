"""Apply coords from hotspot PNGs to sl5-hotspots.json, keyed by zone number."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
COORDS_PATH = ROOT / "private/sl5-hotspot-png-coords.json"


def main() -> None:
    zones = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    coords = json.loads(COORDS_PATH.read_text(encoding="utf-8"))
    by_zone = {c["zone"]: c for c in coords}

    updated = 0
    for z in zones:
        key = str(z.get("zone", "")).zfill(2)
        if key not in by_zone:
            print(f"WARNING: no PNG coords for zone {key} ({z.get('title')})")
            continue
        c = by_zone[key]
        z["x"], z["y"], z["w"], z["h"] = c["x"], c["y"], c["w"], c["h"]
        updated += 1

    zones.sort(key=lambda item: str(item.get("zone", "")).zfill(2))
    JSON_PATH.write_text(json.dumps(zones, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated} zone coords in {JSON_PATH.name}")


if __name__ == "__main__":
    main()
