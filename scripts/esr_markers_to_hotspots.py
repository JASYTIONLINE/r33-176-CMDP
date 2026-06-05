"""
Deprecated: marker-based geometry. Use scripts/esr_sl5_yellow_hotspots.py instead.
Build sl5-hotspots.json from 5x5px red (TL) and blue (BR) corner markers on img-slide-5.png.
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
DEBUG_PATH = ROOT / "private/esr-sl5-markers-debug.png"

# Titles in top-to-bottom, left-to-right order on the slide
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

# 5x5 marker tolerances (anti-aliased export)
MARKER_MIN_AREA = 12
MARKER_MAX_AREA = 40
MARKER_MIN_SIDE = 4
MARKER_MAX_SIDE = 7

BODY_DEFAULTS: dict[str, str] = {}


def load_bodies() -> None:
    if JSON_PATH.exists():
        for item in json.loads(JSON_PATH.read_text(encoding="utf-8")):
            BODY_DEFAULTS[item["title"]] = item["body"]
    BODY_DEFAULTS.setdefault(
        "WO WORK CENTER",
        "Work order work center identifies the maintenance activity or shop responsible "
        "for the repair action. It tells leaders which maintenance organization owns "
        "execution on the work order.",
    )
    BODY_DEFAULTS.setdefault(
        "OPST",
        "Operational status shows the equipment's mission capability condition, such as "
        "NMCS or NMCM. It tells leaders whether the primary delay is maintenance "
        "execution, parts, or another factor driving non-mission-ready status.",
    )


def is_marker_cluster(bw: int, bh: int, area: int) -> bool:
    return (
        MARKER_MIN_AREA <= area <= MARKER_MAX_AREA
        and MARKER_MIN_SIDE <= bw <= MARKER_MAX_SIDE
        and MARKER_MIN_SIDE <= bh <= MARKER_MAX_SIDE
    )


def cluster_markers(mask: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    """Return list of (minx, miny, maxx, maxy, area) for 5px marker squares only."""
    h, w = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    out: list[tuple[int, int, int, int, int]] = []

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            visited[y, x] = True
            minx = maxx = x
            miny = maxy = y
            n = 0
            while q:
                cx, cy = q.popleft()
                n += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        q.append((nx, ny))
            bw, bh = maxx - minx + 1, maxy - miny + 1
            if is_marker_cluster(bw, bh, n):
                out.append((minx, miny, maxx, maxy, n))

    return out


def pair_markers(
    reds: list[tuple[int, int, int, int, int]],
    blues: list[tuple[int, int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    """
    Optimal one-to-one assignment (minimum total box area) between red TL and
    blue BR markers. Invalid pairings get a large penalty cost.
    """
    try:
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        linear_sum_assignment = None  # type: ignore

    n_r, n_b = len(reds), len(blues)
    big = 10_000_000
    cost = np.full((n_r, n_b), big, dtype=np.float64)

    for ri, (rx, ry, *_rest) in enumerate(reds):
        for bi, (bx0, by0, bx1, by1, *_rest) in enumerate(blues):
            if bx0 <= rx or by0 <= ry:
                continue
            bw, bh = bx1 - rx + 1, by1 - ry + 1
            if 12 <= bw <= 520 and 8 <= bh <= 200:
                cost[ri, bi] = bw * bh

    pairs: list[tuple[int, int, int, int]] = []

    if linear_sum_assignment is not None:
        row_ind, col_ind = linear_sum_assignment(cost)
        for ri, bi in zip(row_ind, col_ind):
            if cost[ri, bi] >= big:
                continue
            rx, ry = reds[ri][0], reds[ri][1]
            bx1, by1 = blues[bi][2], blues[bi][3]
            pairs.append((rx, ry, bx1, by1))
    else:
        # Fallback: greedy smallest area
        candidates: list[tuple[int, int, int, int, int, int, int, int]] = []
        for ri, (rx, ry, *_r) in enumerate(reds):
            for bi, (bx0, by0, bx1, by1, *_b) in enumerate(blues):
                if bx0 <= rx or by0 <= ry:
                    continue
                bw, bh = bx1 - rx + 1, by1 - ry + 1
                if 12 <= bw <= 520 and 8 <= bh <= 200:
                    candidates.append((bw * bh, ri, bi, rx, ry, bx1, by1))
        candidates.sort(key=lambda c: c[0])
        used_r: set[int] = set()
        used_b: set[int] = set()
        for _area, ri, bi, rx, ry, bx1, by1 in candidates:
            if ri in used_r or bi in used_b:
                continue
            used_r.add(ri)
            used_b.add(bi)
            pairs.append((rx, ry, bx1, by1))

    return pairs


def build_zones() -> tuple[int, int, list[dict], int, int]:
    im = Image.open(IMAGE_PATH)
    arr = np.array(im.convert("RGB"))
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # User-placed markers (~236,28,36) red and blue BR squares
    red_px = (r > 220) & (g < 90) & (b < 90)
    blue_px = (b > 200) & (r < 100) & (g < 100)

    reds = cluster_markers(red_px)
    blues = cluster_markers(blue_px)
    pairs = pair_markers(reds, blues)

    zones: list[dict] = []
    for x0, y0, x1, y1 in pairs:
        zones.append(
            {
                "x": round(x0 / w * 100, 2),
                "y": round(y0 / h * 100, 2),
                "w": round((x1 - x0 + 1) / w * 100, 2),
                "h": round((y1 - y0 + 1) / h * 100, 2),
                "_x0": x0,
                "_y0": y0,
                "_x1": x1,
                "_y1": y1,
            }
        )

    zones.sort(key=lambda z: (z["y"], z["x"]))

    if len(zones) == len(TITLES_ORDERED):
        for z, title in zip(zones, TITLES_ORDERED):
            z["title"] = title
    else:
        for i, z in enumerate(zones, 1):
            z["title"] = TITLES_ORDERED[i - 1] if i <= len(TITLES_ORDERED) else f"FIELD_{i}"

    debug = im.copy()
    draw = ImageDraw.Draw(debug)
    for i, z in enumerate(zones, 1):
        draw.rectangle((z["_x0"], z["_y0"], z["_x1"], z["_y1"]), outline="lime", width=2)
        label = f"{i}:{z['title'][:10]}"
        draw.text((z["_x0"] + 2, z["_y0"] + 2), label, fill="lime")
    for m in reds:
        draw.rectangle((m[0], m[1], m[2], m[3]), outline="red", width=1)
    for m in blues:
        draw.rectangle((m[0], m[1], m[2], m[3]), outline="blue", width=1)

    DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
    debug.save(DEBUG_PATH)

    for z in zones:
        for k in ("_x0", "_y0", "_x1", "_y1"):
            z.pop(k, None)

    return w, h, zones, len(reds), len(blues)


def assign_bodies(zones: list[dict]) -> list[dict]:
    out: list[dict] = []
    desc_n = 0
    for z in zones:
        title = z["title"]
        if title == "DESCRIPTION":
            desc_n += 1
            if desc_n == 1:
                body = (
                    "On the work order line, description states the fault or repair requirement "
                    "driving the maintenance action. Leaders use it to understand the operational "
                    "problem behind the status and to judge urgency and resource needs."
                )
            else:
                body = (
                    "On the parts line, description identifies the material or part associated "
                    "with the requirement. It helps confirm the correct item is on order or "
                    "issued and supports conversations with supply about pacing parts."
                )
        else:
            body = BODY_DEFAULTS.get(
                title,
                f"This field explains the ESR header {title} and how leaders use it for readiness decisions.",
            )
        out.append({"title": title, "x": z["x"], "y": z["y"], "w": z["w"], "h": z["h"], "body": body})
    return out


def main() -> None:
    load_bodies()
    img_w, img_h, zones, n_red, n_blue = build_zones()
    print(f"Image {img_w}x{img_h}")
    print(f"5px red markers: {n_red}, 5px blue markers: {n_blue}, paired hotspots: {len(zones)}")
    for i, z in enumerate(zones, 1):
        print(f"  {i:2d}  {z['title']:24s}  x={z['x']} y={z['y']} w={z['w']} h={z['h']}")

    if len(zones) != len(TITLES_ORDERED):
        print(
            f"WARNING: expected {len(TITLES_ORDERED)} hotspots; got {len(zones)}. "
            "Check debug image or marker colors on PNG."
        )

    final = assign_bodies(zones)
    JSON_PATH.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {JSON_PATH}")
    print(f"Debug: {DEBUG_PATH}")


if __name__ == "__main__":
    main()
