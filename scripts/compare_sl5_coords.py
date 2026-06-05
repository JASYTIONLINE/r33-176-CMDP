"""Compare current sl5-hotspots.json coords to yellow-box detections per zone."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.esr_sl5_yellow_hotspots import detect_regions

JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
OUT_PATH = ROOT / "private/sl5-coord-correction-table.json"


def center(z: dict) -> tuple[float, float]:
    return (z["x"] + z["w"] / 2, z["y"] + z["h"] / 2)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def match_by_nearest_current(
    detected: list[dict], current_by_zone: dict[str, dict]
) -> dict[str, tuple[dict, float]]:
    """Greedy: each zone gets nearest unused yellow box to its current center."""
    zone_ids = sorted(current_by_zone.keys(), key=lambda k: int(k))
    pairs: list[tuple[float, str, int]] = []
    for zid in zone_ids:
        cc = center(current_by_zone[zid])
        for i, d in enumerate(detected):
            pairs.append((dist(cc, center(d)), zid, i))
    pairs.sort(key=lambda t: t[0])

    assigned_zones: set[str] = set()
    assigned_dets: set[int] = set()
    result: dict[str, tuple[dict, float]] = {}
    for dval, zid, idx in pairs:
        if zid in assigned_zones or idx in assigned_dets:
            continue
        assigned_zones.add(zid)
        assigned_dets.add(idx)
        result[zid] = (detected[idx], dval)
    return result


def main() -> None:
    current = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    current_by_zone = {z["zone"]: z for z in current}

    _, _, detected = detect_regions()
    matched = match_by_nearest_current(detected, current_by_zone)

    rows = []
    print(
        f"{'zone':>4}  {'title':<20}  "
        f"{'cur_x':>6} {'cur_y':>6} {'cur_w':>6} {'cur_h':>6}  "
        f"{'new_x':>6} {'new_y':>6} {'new_w':>6} {'new_h':>6}  "
        f"{'d_x':>6} {'d_y':>6} {'d_w':>6} {'d_h':>6}  "
        f"{'TL_x':>5} {'TL_y':>5} {'BR_x':>5} {'BR_y':>5}  match"
    )
    print("-" * 135)

    for zid in sorted(current_by_zone.keys(), key=lambda k: int(k)):
        cur = current_by_zone[zid]
        hit = matched.get(zid)
        if not hit:
            print(f"{zid:>4}  {cur['title'][:20]:<20}  NO YELLOW MATCH")
            continue

        det, match_dist = hit
        dx = round(det["x"] - cur["x"], 2)
        dy = round(det["y"] - cur["y"], 2)
        dw = round(det["w"] - cur["w"], 2)
        dh = round(det["h"] - cur["h"], 2)

        quality = "ok" if match_dist < 5 else "CHECK"

        row = {
            "zone": zid,
            "title": cur["title"],
            "match_dist_pct": round(match_dist, 2),
            "match_quality": quality,
            "current": {"x": cur["x"], "y": cur["y"], "w": cur["w"], "h": cur["h"]},
            "detected_yellow": {"x": det["x"], "y": det["y"], "w": det["w"], "h": det["h"]},
            "detected_px": {
                "tl_x": det["_x0"],
                "tl_y": det["_y0"],
                "br_x": det["_x1"],
                "br_y": det["_y1"],
            },
            "delta": {"x": dx, "y": dy, "w": dw, "h": dh},
            "recommended": {"x": det["x"], "y": det["y"], "w": det["w"], "h": det["h"]},
        }
        rows.append(row)

        flag = " ***" if quality == "CHECK" else ""
        print(
            f"{zid:>4}  {cur['title'][:20]:<20}  "
            f"{cur['x']:>6} {cur['y']:>6} {cur['w']:>6} {cur['h']:>6}  "
            f"{det['x']:>6} {det['y']:>6} {det['w']:>6} {det['h']:>6}  "
            f"{dx:>+6} {dy:>+6} {dw:>+6} {dh:>+6}  "
            f"{det['_x0']:>5} {det['_y0']:>5} {det['_x1']:>5} {det['_y1']:>5}  {match_dist:>5.1f}{flag}"
        )

    OUT_PATH.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")
    print("*** = match distance > 5% — verify zone pairing on esr-sl5-yellow-debug.png")


if __name__ == "__main__":
    main()
