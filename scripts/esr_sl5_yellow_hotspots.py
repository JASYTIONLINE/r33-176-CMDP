"""
Build sl5-hotspots.json from yellow-filled boxes with black borders on img-slide-5.png.
Assigns titles in top-to-bottom, left-to-right order (TITLES_ORDERED).
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT / "assets/images/esr-class/img-slide-5.png"
JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
BODIES_BACKUP = ROOT / "private/sl5-hotspots-bodies-backup.json"
DEBUG_PATH = ROOT / "private/esr-sl5-yellow-debug.png"

TITLES_ORDERED = [
    "REPORT FILTERS",
    "DATE/TIME OF REPORT",
    "MODEL",
    "ADMIN NO.",
    "SERIAL NO.",
    "OPST",
    "EQ DESCRIPTION",
    "DL ST DATE/TIME",
    "DAYS DL",
    "UIC",
    "UIC DESCRIPTION",
    "REPORTABLE DL EQ",
    "ORDER NO.",
    "DESCRIPTION",
    "SC-DATE",
    "PRT-ORD-DT",
    "NIIN",
    "DESCRIPTION",
    "STAT",
    "SC",
    "WO WORK CENTER",
    "ERC",
    "Q-ORD",
    "Q-ISS",
    "Q-OH",
    "Q-NL",
    "SOS",
    "REF DOC",
    "ST",
    "DATE/TIME",
]

# Yellow/black detection tuned for 2000x1600 export
MIN_AREA = 55
MIN_BW = 8
MIN_BH = 8
BLACK_MIN = 40
PAD = 4

DESCRIPTION_BODIES = (
    (
        "On the work order line, description states the fault or repair requirement "
        "driving the maintenance action. Leaders use it to understand the operational "
        "problem behind the status and to judge urgency and resource needs."
    ),
    (
        "On the parts line, description identifies the material or part associated "
        "with the requirement. It helps confirm the correct item is on order or "
        "issued and supports conversations with supply about pacing parts."
    ),
)


def load_body_defaults() -> dict[str, str]:
    bodies: dict[str, str] = {}
    for path in (BODIES_BACKUP, JSON_PATH):
        if not path.exists():
            continue
        for item in json.loads(path.read_text(encoding="utf-8")):
            text = item.get("body", "")
            if text and not text.startswith("This field explains the ESR header"):
                bodies[item["title"]] = text
    bodies.setdefault(
        "DAYS DL",
        "Days deadlined quantifies how long the equipment has been in a deadlined status "
        "on this entry. It is a primary field for leader prioritization because long "
        "durations often signal stalled maintenance, parts, or follow-up problems.",
    )
    bodies.setdefault(
        "WO WORK CENTER",
        "Work order work center identifies the maintenance activity or shop responsible "
        "for the repair action. It tells leaders which maintenance organization owns "
        "execution on the work order.",
    )
    return bodies


def _box_from_pixels(minx: int, miny: int, maxx: int, maxy: int, img_w: int, img_h: int) -> dict:
    bw, bh = maxx - minx + 1, maxy - miny + 1
    return {
        "x": round(minx / img_w * 100, 2),
        "y": round(miny / img_h * 100, 2),
        "w": round(bw / img_w * 100, 2),
        "h": round(bh / img_h * 100, 2),
        "_x0": minx,
        "_y0": miny,
        "_x1": maxx,
        "_y1": maxy,
    }


def split_opst_and_days_dl(zones: list[dict], img_w: int, img_h: int) -> list[dict]:
    """Split merged far-right equipment row blob into OPST and DAYS DL."""
    out: list[dict] = []
    for z in zones:
        if z["y"] < 37 or z["y"] > 42 or z["x"] < 88 or z["w"] < 4:
            out.append(z)
            continue
        x0, y0, x1, y1 = z["_x0"], z["_y0"], z["_x1"], z["_y1"]
        mid = x0 + int((x1 - x0) * 0.55)
        out.append(_box_from_pixels(x0, y0, mid, y1, img_w, img_h))
        out.append(_box_from_pixels(mid + 1, y0, x1, y1, img_w, img_h))
    return out


def detect_regions() -> tuple[int, int, list[dict]]:
    im = Image.open(IMAGE_PATH).convert("RGB")
    arr = np.array(im)
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    yellow = (r >= 235) & (g >= 235) & (b >= 140) & (b <= 230)
    black = (r < 60) & (g < 60) & (b < 60)

    visited = np.zeros(yellow.shape, dtype=bool)
    raw: list[tuple[int, int, int, int]] = []

    for y in range(h):
        for x in range(w):
            if not yellow[y, x] or visited[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            visited[y, x] = True
            minx = maxx = x
            miny = maxy = y
            area = 0
            while q:
                cx, cy = q.popleft()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and yellow[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        q.append((nx, ny))
            bw, bh = maxx - minx + 1, maxy - miny + 1
            if area < MIN_AREA or bw < MIN_BW or bh < MIN_BH:
                continue
            y0, y1 = max(0, miny - PAD), min(h, maxy + PAD + 1)
            x0, x1 = max(0, minx - PAD), min(w, maxx + PAD + 1)
            if black[y0:y1, x0:x1].sum() < BLACK_MIN:
                continue
            raw.append((minx, miny, maxx, maxy))

    zones: list[dict] = []
    for minx, miny, maxx, maxy in raw:
        bw, bh = maxx - minx + 1, maxy - miny + 1
        zones.append(
            {
                "x": round(minx / w * 100, 2),
                "y": round(miny / h * 100, 2),
                "w": round(bw / w * 100, 2),
                "h": round(bh / h * 100, 2),
                "_x0": minx,
                "_y0": miny,
                "_x1": maxx,
                "_y1": maxy,
            }
        )

    zones.sort(key=lambda z: (z["y"], z["x"]))
    zones = split_opst_and_days_dl(zones, w, h)
    zones = [
        z
        for z in zones
        if not (abs(z["x"] - 31.2) < 0.2 and abs(z["y"] - 38.0) < 0.2)
    ]
    zones.sort(key=lambda z: (z["y"], z["x"]))

    for manual in MANUAL_ZONES:
        if any(
            abs(z["x"] - manual["x"]) < XY_MATCH_TOLERANCE
            and abs(z["y"] - manual["y"]) < XY_MATCH_TOLERANCE
            for z in zones
        ):
            continue
        x0 = int(manual["x"] / 100 * w)
        y0 = int(manual["y"] / 100 * h)
        x1 = int((manual["x"] + manual["w"]) / 100 * w) - 1
        y1 = int((manual["y"] + manual["h"]) / 100 * h) - 1
        zones.append({**manual, "_x0": x0, "_y0": y0, "_x1": x1, "_y1": y1})

    zones.sort(key=lambda z: (z["y"], z["x"]))
    return w, h, zones


# (x%, y%) -> title from yellow-box detection on img-slide-5.png (2000x1600)
TITLE_BY_XY: dict[tuple[float, float], str] = {
    (1.05, 15.5): "REPORT FILTERS",
    (40.55, 19.19): "DATE/TIME OF REPORT",
    (4.15, 37.5): "MODEL",
    (15.6, 38.0): "DL ST DATE/TIME",
    (31.45, 38.38): "ADMIN NO.",
    (50.75, 38.5): "SERIAL NO.",
    (78.15, 38.44): "EQ DESCRIPTION",
    (45.65, 38.5): "OPST",
    (95.95, 37.88): "DAYS DL",
    (55.55, 45.0): "REPORTABLE DL EQ",
    (13.35, 45.44): "UIC DESCRIPTION",
    (2.25, 46.94): "UIC",
    (16.9, 54.19): "ORDER NO.",
    (25.35, 59.38): "PRT-ORD-DT",
    (33.9, 59.75): "SC-DATE",
    (40.1, 59.75): "NIIN",
    (73.15, 60.75): "ERC",
    (26.45, 60.81): "DESCRIPTION",
    (28.4, 60.81): "SC",
    (5.9, 65.56): "STAT",
    (45.95, 68.5): "WO WORK CENTER",
    (86.35, 78.5): "Q-ORD",
    (89.25, 78.5): "REF DOC",
    (78.5, 78.56): "SOS",
    (72.65, 79.44): "ST",
    (65.4, 81.31): "Q-NL",
    (57.3, 81.62): "Q-OH",
    (62.0, 86.38): "Q-ISS",
    (68.7, 86.5): "DATE/TIME",
}

XY_MATCH_TOLERANCE = 1.2

# Parts-line DESCRIPTION (yellow box not isolated by flood fill on this export)
MANUAL_ZONES: list[dict] = [
    {
        "title": "DESCRIPTION",
        "x": 56.5,
        "y": 59.75,
        "w": 15.5,
        "h": 2.62,
        "_desc_index": 1,
    },
]


def assign_titles(zones: list[dict]) -> None:
    for z in zones:
        if "title" in z:
            continue
        for (rx, ry), title in TITLE_BY_XY.items():
            if abs(z["x"] - rx) <= XY_MATCH_TOLERANCE and abs(z["y"] - ry) <= XY_MATCH_TOLERANCE:
                z["title"] = title
                break
        else:
            z["title"] = f"UNMAPPED_{z['x']}_{z['y']}"

    missing = set(TITLES_ORDERED) - {z["title"] for z in zones}
    if missing:
        print(f"WARNING: unassigned titles: {sorted(missing)}")
    extra = [z["title"] for z in zones if z["title"] not in TITLES_ORDERED]
    if extra:
        print(f"WARNING: unknown titles: {extra}")


def assign_bodies(zones: list[dict], defaults: dict[str, str]) -> list[dict]:
    out: list[dict] = []
    desc_n = 0
    for z in sorted(zones, key=lambda item: (item["y"], item["x"])):
        title = z["title"]
        if title == "DESCRIPTION":
            idx = z.get("_desc_index", 0 if z["y"] >= 60 else 1)
            body = DESCRIPTION_BODIES[min(idx, 1)]
            desc_n += 1
        else:
            body = defaults.get(
                title,
                f"This field explains the ESR header {title} and how leaders use it "
                "for readiness decisions.",
            )
        out.append(
            {
                "title": title,
                "x": z["x"],
                "y": z["y"],
                "w": z["w"],
                "h": z["h"],
                "body": body,
            }
        )
    return out


def save_debug(img_w: int, img_h: int, zones: list[dict]) -> None:
    im = Image.open(IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(im)
    for i, z in enumerate(zones, 1):
        draw.rectangle((z["_x0"], z["_y0"], z["_x1"], z["_y1"]), outline="lime", width=2)
        label = f"{i}:{z['title'][:12]}"
        draw.text((z["_x0"] + 2, z["_y0"] + 2), label, fill="lime")
    DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
    im.save(DEBUG_PATH)


def main() -> None:
    defaults = load_body_defaults()
    img_w, img_h, zones = detect_regions()
    print(f"Image {img_w}x{img_h}, yellow boxes: {len(zones)}")
    assign_titles(zones)
    for i, z in enumerate(zones, 1):
        print(f"  {i:2d}  {z['title']:24s}  x={z['x']} y={z['y']} w={z['w']} h={z['h']}")

    save_debug(img_w, img_h, zones)
    for z in zones:
        for k in ("_x0", "_y0", "_x1", "_y1"):
            z.pop(k, None)

    final = assign_bodies(zones, defaults)
    JSON_PATH.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {JSON_PATH}")
    print(f"Debug: {DEBUG_PATH}")


if __name__ == "__main__":
    main()
