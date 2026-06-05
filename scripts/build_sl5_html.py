"""Build sl5-reading-esr.html hotspot buttons from sl5-hotspots.json."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
json_path = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
out_path = ROOT / "content/esr-class/esr/main/sl5-reading-esr.html"

zones = json.loads(json_path.read_text(encoding="utf-8"))
zones.sort(key=lambda item: str(item.get("zone", "")).zfill(2))
buttons = []
for z in zones:
    title = html.escape(z["title"], quote=True)
    body = html.escape(z["body"], quote=True)
    zone_id = html.escape(str(z.get("zone", "")), quote=True)
    buttons.append(
        f'            <button class="slide-hotspot" type="button" '
        f'style="--zone-x: {z["x"]}%; --zone-y: {z["y"]}%; '
        f'--zone-w: {z["w"]}%; --zone-h: {z["h"]}%;" '
        f'data-zone="{zone_id}" data-zone-title="{title}" data-zone-body="{body}">'
        f'<span class="visually-hidden">{title}</span></button>'
    )

hotspot_html = "\n".join(buttons)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reading the ESR</title>
  <link rel="stylesheet" href="../../css/styles.css">
</head>
<body>
  <header class="site-header">
    <nav class="top-nav" aria-label="CMDP and ESR class navigation">
      <span class="brand brand-primary">Maintenance is Readiness</span>
      <div class="nav-links">
        <div class="nav-links-main">
          <a href="sl1-esr-key.html" data-slide="1"><span>Equipment Situation Report</span><span>Familiarization</span></a>
          <a href="../../gcssa/sl12-gcssa-access-esr.html" data-slide="12"><span>How to access the ESR</span><span>in GCSS-A</span></a>
          <a href="../../references/sl15-ref-esr-legend.html" data-slide="15">References</a>
        </div>
        <a href="../../../../index.html" class="nav-exit-cmdp">Back to CMDP</a>
      </div>
    </nav>
  </header>
<main class="slide-shell" data-current-slide="5" data-slide-audio="/assets/audio/slide5.mp3">
    <section class="slide-card" aria-labelledby="slide-title">
<h1 id="slide-title">Reading the ESR</h1>
      <div class="slide-figure">
        <a class="slide-arrow slide-arrow-left" href="sl4-status-decisions.html" aria-label="Previous page"></a>
        <div class="slide-image-wrap">
          <img class="slide-image" src="../../../../assets/images/esr-class/img-slide-5.png" alt="Slide 5: Reading the ESR — interactive field guide">
          <div class="slide-hotspot-layer" aria-label="Interactive ESR information zones">
{hotspot_html}
          </div>
        </div>
        <a class="slide-arrow slide-arrow-right" href="sl6-operational-codes.html" aria-label="Next page"></a>
      </div>

      <div class="slide-copy">
        <p>This is the practical layout for reading an ESR. The yellow boxes on the sample report mark the fields leaders need most: equipment identity, operational status, work order details, repair status, parts movement, and time in deadline status.</p>
        <p><strong>Interactive:</strong> Click inside any yellow box on the image for a full explanation of what that ESR header means and how to use it in readiness decisions.</p>
      </div>
    </section>
  </main>
  <footer class="slide-page-footer" aria-label="Slide position">
    <p class="slide-footer-meta">Equipment Status Report Class | Page 5 of 15</p>
  </footer>

  <div class="zone-modal" data-zone-modal hidden>
    <div class="zone-modal-backdrop" data-zone-modal-close></div>
    <section class="zone-modal-panel" role="dialog" aria-modal="true" aria-labelledby="zone-modal-title" aria-describedby="zone-modal-body">
      <button class="zone-modal-close" type="button" data-zone-modal-close aria-label="Close modal"></button>
      <h2 id="zone-modal-title"></h2>
      <p id="zone-modal-body"></p>
    </section>
  </div>

  <script src="../../js/app.js"></script>
</body>
</html>
"""

out_path.write_text(page, encoding="utf-8", newline="\n")
print(f"Wrote {out_path.name} with {len(zones)} hotspots")
