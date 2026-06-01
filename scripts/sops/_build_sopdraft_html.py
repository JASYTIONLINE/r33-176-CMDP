"""SOP draft pipeline: add Draft Notice to canonical sops/10*-sop*.html when missing, then masthead enhancer."""
from __future__ import annotations

import re

from scripts.paths import sop_publish_dir

ROOT = sop_publish_dir()

STYLE_BLOCK = """    <style>
    .draft-banner { background:#fff4d6; border:1px solid #e5c878; border-left:6px solid #c99700; border-radius:4px; padding:1rem; margin:0 0 1.25rem; }
    .draft-banner p { margin:.25rem 0; }
    @media print { .draft-banner { display:none !important; } }
    </style>
"""

DRAFT_BANNER_SIMPLE = """      <!-- DRAFT BLOCK START: remove this section when approved -->
      <section id="draft-banner" class="draft-banner">
        <h2>Draft Notice</h2>
        <p><strong>Status:</strong> Draft for review and coordination.</p>
        <p>Delete this entire block on approval to publish as final.</p>
      </section>

"""

TITLE_RE = re.compile(r"<title>([^<]*)</title>")


def ensure_draft_title(html: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        return html
    title_inner = m.group(1).strip()
    if "(Draft)" in title_inner:
        return html
    if title_inner.endswith(" - CMDP Compliance"):
        title_new = title_inner.replace(" - CMDP Compliance", " (Draft) - CMDP Compliance", 1)
    else:
        title_new = f"{title_inner} (Draft)"
    return TITLE_RE.sub(f"<title>{title_new}</title>", html, count=1)


def ensure_draft_styles(html: str) -> str:
    if ".draft-banner" in html and "@media print" in html:
        idx = html.find(".draft-banner { display:none")
        if idx == -1 and "draft-banner" in html:
            if "</style>" not in html:
                html = html.replace("</head>", f"{STYLE_BLOCK}</head>")
            elif ".draft-banner" in html.split("</head>", 1)[0]:
                html = html.replace("</style>", f"\n    @media print {{ .draft-banner {{ display:none !important; }} }}\n  </style>", 1)
        return html
    if "</head>" not in html:
        return html
    return html.replace("</head>", f"{STYLE_BLOCK}</head>", 1)


def inject_draft_banner(html: str) -> str:
    if 'id="draft-banner"' in html:
        return html
    m_shell = re.search(r"(<main>\s*\n)(\s*)(<section\s+[^>]*class=\"sop-shell\"[^>]*>)", html)
    if m_shell:
        return html[: m_shell.end()] + "\n" + DRAFT_BANNER_SIMPLE + html[m_shell.end() :]
    m_main = re.search(r"<main\b[^>]*>", html)
    if not m_main:
        return html
    insert_pos = m_main.end()
    return html[:insert_pos] + "\n" + DRAFT_BANNER_SIMPLE + html[insert_pos:]


def ensure_canonical_sop_banners() -> None:
    """Inject Draft Notice + styles into sops/*.html canonical pages that lack them."""
    for path in sorted(ROOT.glob("10.*-sop*.html")):
        html = path.read_text(encoding="utf-8")
        if 'id="draft-banner"' in html:
            continue
        html = ensure_draft_styles(html)
        html = inject_draft_banner(html)
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"Added draft banner (canonical): {path.name}")


def main() -> None:
    ensure_canonical_sop_banners()
    try:
        from scripts.sops import _enhance_sopdraft_pages as _enh

        _enh.main()
    except Exception as exc:
        print(f"Note: SOP masthead enhance skipped ({exc})")


if __name__ == "__main__":
    main()
