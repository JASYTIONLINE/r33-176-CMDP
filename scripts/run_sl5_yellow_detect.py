"""Detect yellow boxes on img-slide-5.png; report pixel coords matched to zone numbers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw

from scripts.esr_sl5_yellow_hotspots import IMAGE_PATH, detect_regions

JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
OUT_PATH = ROOT / "private/sl5-yellow-detect.json"


def center(z: dict) -> tuple[float, float]:
    return (z["x"] + z["w"] / 2, z["y"] + z["h"] / 2)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def main() -> None:
    zones_json = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_zone = {z["zone"]: z for z in zones_json}

    w, h, detected = detect_regions()
    debug = Image.open(IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(debug)
    for i, d in enumerate(detected, 1):
        draw.rectangle((d["_x0"], d["_y0"], d["_x1"], d["_y1"]), outline="lime", width=2)
        draw.text((d["_x0"] + 2, d["_y0"] + 2), str(i), fill="lime")
    debug_path = ROOT / "private/esr-sl5-yellow-debug.png"
    debug_path.parent.mkdir(parents=True, exist_ok=True)
    debug.save(debug_path)

    print(f"Image: {w}x{h}px")
    print(f"Yellow boxes detected: {len(detected)}")
    print()

    used: set[int] = set()
    rows: list[dict] = []
    for zid in sorted(by_zone.keys(), key=lambda k: int(k)):
        zj = by_zone[zid]
        jc = center(zj)
        best_i, best_d = None, 1e9
        for i, d in enumerate(detected):
            if i in used:
                continue
            dd = dist(jc, center(d))
            if dd < best_d:
                best_d, best_i = dd, i

        entry: dict = {
            "zone": zid,
            "title": zj["title"],
            "match_dist_pct": round(best_d, 2) if best_i is not None else None,
            "current": {"x": zj["x"], "y": zj["y"], "w": zj["w"], "h": zj["h"]},
        }
        if best_i is not None:
            used.add(best_i)
            d = detected[best_i]
            x0, y0, x1, y1 = d["_x0"], d["_y0"], d["_x1"], d["_y1"]
            entry["detected_px"] = {
                "tl_x": x0,
                "tl_y": y0,
                "br_x": x1,
                "br_y": y1,
                "w_px": x1 - x0 + 1,
                "h_px": y1 - y0 + 1,
            }
            entry["detected"] = {"x": d["x"], "y": d["y"], "w": d["w"], "h": d["h"]}
        rows.append(entry)

    unmatched = []
    for i, d in enumerate(detected):
        if i not in used:
            unmatched.append(
                {
                    "index": i + 1,
                    "tl_x": d["_x0"],
                    "tl_y": d["_y0"],
                    "br_x": d["_x1"],
                    "br_y": d["_y1"],
                    "x": d["x"],
                    "y": d["y"],
                    "w": d["w"],
                    "h": d["h"],
                }
            )

    out = {
        "image_w": w,
        "image_h": h,
        "detected_count": len(detected),
        "zones": rows,
        "unmatched": unmatched,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(
        f"{'zone':>4}  {'title':<22}  {'TL_x':>5} {'TL_y':>5} {'BR_x':>5} {'BR_y':>5}  "
        f"{'w_px':>4} {'h_px':>4}  {'x%':>6} {'y%':>6} {'w%':>6} {'h%':>6}  dist"
    )
    print("-" * 100)
    for r in rows:
        if "detected_px" not in r:
            print(f"{r['zone']:>4}  {r['title'][:22]:<22}  NO MATCH")
            continue
        p, d = r["detected_px"], r["detected"]
        print(
            f"{r['zone']:>4}  {r['title'][:22]:<22}  "
            f"{p['tl_x']:>5} {p['tl_y']:>5} {p['br_x']:>5} {p['br_y']:>5}  "
            f"{p['w_px']:>4} {p['h_px']:>4}  "
            f"{d['x']:>6} {d['y']:>6} {d['w']:>6} {d['h']:>6}  {r['match_dist_pct']}"
        )

    if unmatched:
        print()
        print("Unmatched yellow boxes:")
        for u in unmatched:
            print(
                f"  #{u['index']}: TL=({u['tl_x']},{u['tl_y']}) BR=({u['br_x']},{u['br_y']})  "
                f"x={u['x']} y={u['y']} w={u['w']} h={u['h']}"
            )

    print()
    print("All detections in scan order (top-to-bottom, left-to-right):")
    print(f"{'idx':>3}  {'TL_x':>5} {'TL_y':>5} {'BR_x':>5} {'BR_y':>5}  {'w_px':>4} {'h_px':>4}  {'x%':>6} {'y%':>6} {'w%':>6} {'h%':>6}")
    for i, d in enumerate(detected, 1):
        print(
            f"{i:>3}  {d['_x0']:>5} {d['_y0']:>5} {d['_x1']:>5} {d['_y1']:>5}  "
            f"{d['_x1'] - d['_x0'] + 1:>4} {d['_y1'] - d['_y0'] + 1:>4}  "
            f"{d['x']:>6} {d['y']:>6} {d['w']:>6} {d['h']:>6}"
        )

    print(f"\nWrote {OUT_PATH}")
    print(f"Debug overlay: private/esr-sl5-yellow-debug.png")


if __name__ == "__main__":
    main()
