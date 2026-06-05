"""Detect yellow hotspot boxes on slide 5; rebuild sl5-hotspots.json."""
from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from esr_sl5_yellow_hotspots import main

    main()
