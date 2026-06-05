"""One-off: extract sl5-hotspots.json bodies from agent transcript line."""
from __future__ import annotations

import json
import re
from pathlib import Path

TRANSCRIPT = Path(
    r"C:\Users\johnb\.cursor\projects\c-lt-c-files-shared-files-08-github-r33-176-CMDP\agent-transcripts"
    r"\f5aa1ba2-f27d-476c-8056-ed86f87ed69d\f5aa1ba2-f27d-476c-8056-ed86f87ed69d.jsonl"
)
OUT = Path(__file__).resolve().parents[1] / "private/sl5-hotspots-bodies-backup.json"


def main() -> None:
    line = TRANSCRIPT.read_text(encoding="utf-8").splitlines()[841]
    # Unescape JSON embedded in tool Write "contents": "[...]"
    m = re.search(r'"contents": "(\[)', line)
    if not m:
        raise SystemExit("Could not find JSON start in transcript line")
    start = m.start(1)
    raw = line[start:]
    # Walk escaped string until closing unescaped "
    out = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt == "n":
                out.append("\n")
            elif nxt == '"':
                out.append('"')
            elif nxt == "\\":
                out.append("\\")
            else:
                out.append(nxt)
            i += 2
            continue
        if ch == '"' and out:
            break
        out.append(ch)
        i += 1
    text = "".join(out)
    zones = json.loads(text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(zones, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(zones)} zones to {OUT}")


if __name__ == "__main__":
    main()
