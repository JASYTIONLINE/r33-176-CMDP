"""Post-process sops/10.*-sop*.html: masthead, dynamic title + Word-only actions.

Run after _build_sopdraft_html.py (or standalone). Skips 10.1.6.7.8-sop-maintenance.html.
"""
from __future__ import annotations

import re
from pathlib import Path

from scripts.paths import sop_publish_dir

ROOT = sop_publish_dir()
SKIP = "10.1.6.7.8-sop-maintenance.html"

SUPPLEMENT_STYLE = """
    <style id="sopdraft-masthead-style">
    .sop-actions { display:flex; flex-wrap:wrap; justify-content: center; gap:.75rem; margin: 0 0 1rem 0; }
    .sop-actions a { border: 0; }
    header h1 .site-doc-title-dynamic { font-size: 1.1rem; font-weight: normal; }
    @media (max-width: 768px) { header h1 .site-doc-title-dynamic { font-size: 1rem; } }
    @media print {
      header, nav, footer, .sop-actions { display: none !important; }
      a[href]:after { content: ""; }
      .back-to-top-float { display: none !important; }
    }
    </style>
"""

SYNC_SCRIPT = r"""
  <script id="sopdraft-doc-badge-sync">
    document.addEventListener("DOMContentLoaded", function () {
      var src = document.getElementById("sop-cover-title-short");
      var dst = document.getElementById("site-compliance-doc-badge");
      if (!src || !dst) return;
      dst.textContent = src.textContent.replace(/\s+/g, " ").trim();
    });
  </script>
"""

HEADER_NEW = '<header><h1>CMDP Compliance Document: <span id="site-compliance-doc-badge" class="site-doc-title-dynamic" aria-live="polite"></span></h1></header>'

HEADER_PAT = re.compile(
    r"<header\s*>\s*<h1>\s*CMDP Compliance Documents\s*</h1>\s*</header\s*>",
    re.IGNORECASE | re.DOTALL,
)


def word_href(filename: str) -> tuple[str, str]:
    stem = Path(filename).stem
    if stem == "10.2.2-sop-dispatch":
        return (
            "../assets/word/memos/10.2.2-sop-dispatch.docx",
            "10.2.2-sop-dispatch.docx",
        )
    return f"../assets/word/sops/{stem}.docx", f"{stem}.docx"


def ensure_supplement_style(html: str) -> str:
    if 'id="sopdraft-masthead-style"' in html:
        return html
    return re.sub(r"(</head\s*>)", SUPPLEMENT_STYLE + r"\1", html, count=1, flags=re.IGNORECASE)


def ensure_sync_script(html: str) -> str:
    if 'id="sopdraft-doc-badge-sync"' in html:
        return html
    needle = '<script src="../static/scripts/site-nav.js"></script>'

    if needle not in html:
        needle = '<script src="../static/scripts/site-nav.js">'  # tolerant

        if needle not in html:
            return html

    idx = html.rfind('<script src="../static/scripts/site-nav.js"></script>')
    if idx == -1:
        idx = html.rfind('<script src="../static/scripts/site-nav.js">')

    return html[:idx] + SYNC_SCRIPT + "\n" + html[idx:]


def replace_header(html: str) -> str:
    return HEADER_PAT.sub(HEADER_NEW, html, count=1)


def wrap_first_main_h1(html: str) -> str:
    if 'id="sop-cover-title-short"' in html:
        return html

    main_i = html.lower().find("<main>")

    if main_i == -1:
        return html

    tail = html[main_i:]
    m = re.search(r"<h1\b[^>]*>\s*(.+?)\s*</h1\s*>", tail, re.DOTALL | re.IGNORECASE)

    if not m:
        return html

    inner = m.group(1).strip()

    if "<span" in inner.lower():
        return html

    full = m.group(0)

    inner_clean = re.sub(r"\s+", " ", inner).strip()

    replacement = f'<h1><span id="sop-cover-title-short">{inner_clean}</span></h1>'

    abs_pos = main_i + tail.find(full)

    return html[:abs_pos] + replacement + html[abs_pos + len(full) :]


def normalize_sop_actions(html: str, filename: str) -> str:
    href, dl = word_href(filename)

    anchor = (
        f'<a class="download-btn" href="{href}" '
        f'download="{dl}">Download Word (AR&nbsp;25-50)</a>'
    )
    block = f'<div class="sop-actions">\n        {anchor}\n      </div>'

    return re.sub(
        r'<div\b[^>]*class="([^"\s]*[^"]*\bsop-actions\b[^\"]*)"[^>]*>.*?</div\s*>',
        block,
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def process_file(path: Path) -> bool:
    if path.name == SKIP:
        return False

    text = path.read_text(encoding="utf-8")

    text = replace_header(text)

    text = ensure_supplement_style(text)

    text = wrap_first_main_h1(text)

    text = normalize_sop_actions(text, path.name)

    text = ensure_sync_script(text)

    path.write_text(text, encoding="utf-8")
    print(f"Enhanced {path.name}")
    return True


def main() -> None:
    count = 0

    for p in sorted(ROOT.glob("10.*-sop*.html")):
        if process_file(p):
            count += 1

    print(f"Done. Updated {count} files (skipped {SKIP}).")


if __name__ == "__main__":
    main()
