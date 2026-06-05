"""Detect zone bounding boxes from isolated hotspot PNGs in assets/images/esr-class/hotspots/."""
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOTSPOTS_DIR = ROOT / "assets/images/esr-class/hotspots"
SLIDE_PATH = ROOT / "assets/images/esr-class/img-slide-5.png"
OUT_PATH = ROOT / "private/sl5-hotspot-png-coords.json"

# Slide canvas used by CSS aspect-ratio 2000 / 1600
SLIDE_W, SLIDE_H = 2000, 1600


def find_largest_black_frame(arr: np.ndarray) -> tuple[int, int, int, int] | None:
    """Return inner content rect (x0,y0,x1,y1) inside thick black border."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    black = (r < 60) & (g < 60) & (b < 60)
    h, w = black.shape
    # Scan for horizontal black lines to find top/bottom frame edges
    row_counts = black.sum(axis=1)
    col_counts = black.sum(axis=0)
    thick = int(w * 0.02)
    rows = np.where(row_counts > w * 0.5)[0]
    cols = np.where(col_counts > h * 0.5)[0]
    if len(rows) < 2 or len(cols) < 2:
        return None
    y0, y1 = int(rows[0]), int(rows[-1])
    x0, x1 = int(cols[0]), int(cols[-1])
    # Shrink to inner white/content area
    return x0 + thick, y0 + thick, x1 - thick, y1 - thick


def find_red_box(arr: np.ndarray, frame: tuple[int, int, int, int]) -> tuple[int, int, int, int] | None:
    fx0, fy0, fx1, fy1 = frame
    sub = arr[fy0:fy1, fx0:fx1]
    r, g, b = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
    red = (r > 180) & (g < 100) & (b < 100)
    h, w = red.shape
    vis = np.zeros((h, w), dtype=bool)
    best = None
    best_area = 0
    for y in range(h):
        for x in range(w):
            if not red[y, x] or vis[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            vis[y, x] = True
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
                    if 0 <= nx < w and 0 <= ny < h and red[ny, nx] and not vis[ny, nx]:
                        vis[ny, nx] = True
                        q.append((nx, ny))
            if area > best_area and (maxx - minx) > 10 and (maxy - miny) > 5:
                best_area = area
                best = (fx0 + minx, fy0 + miny, fx0 + maxx, fy0 + maxy)
    return best


def box_to_pct(box: tuple[int, int, int, int], frame: tuple[int, int, int, int]) -> dict:
    x0, y0, x1, y1 = box
    fx0, fy0, fx1, fy1 = frame
    fw, fh = fx1 - fx0, fy1 - fy0
    return {
        "x": round((x0 - fx0) / fw * 100, 2),
        "y": round((y0 - fy0) / fh * 100, 2),
        "w": round((x1 - x0 + 1) / fw * 100, 2),
        "h": round((y1 - y0 + 1) / fh * 100, 2),
    }


def detect_zone(path: Path) -> dict | None:
    arr = np.array(Image.open(path).convert("RGB"))
    frame = find_largest_black_frame(arr)
    if not frame:
        return None
    box = find_red_box(arr, frame)
    if not box:
        return None
    pct = box_to_pct(box, frame)
    m = re.search(r"z(\d+)", path.stem)
    zone = m.group(1).zfill(2) if m else "?"
    return {"zone": zone, "file": path.name, **pct, "frame": frame, "box_px": box}


def main() -> None:
    results = []
    for path in sorted(HOTSPOTS_DIR.glob("hot-spot-map-z*.png")):
        hit = detect_zone(path)
        if hit:
            results.append(hit)
            print(f"zone {hit['zone']}: x={hit['x']} y={hit['y']} w={hit['w']} h={hit['h']}")
        else:
            print(f"FAILED {path.name}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} zones to {OUT_PATH}")


if __name__ == "__main__":
    main()
