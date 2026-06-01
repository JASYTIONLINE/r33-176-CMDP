"""Build sops/10.10.1-sop-driver-training.html from source/sops/10.10.1-sop-driver-training.md.

Strips erroneous leading backslashes typical of pasted exports; mirrors Ground Maintenance shell
(CSS + sop-shell + cover-block) for Web and Word tooling."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from scripts.paths import repo_root, sop_publish_dir

_REPO = repo_root()
MD_SRC = _REPO / "source" / "sops" / "10.10.1-sop-driver-training.md"
HTML_OUT = sop_publish_dir() / "10.10.1-sop-driver-training.html"

SECTION_RE = re.compile(r"^\d+\-\d+\.\s")

HTML_SHELL_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Driver Training SOP (Draft) - CMDP Compliance</title>
  <link rel="stylesheet" href="../css/styles.css" />
  <style>
    .sop-shell { max-width: 900px; margin: 0 auto; background: #fff; border: 1px solid #d9d9d9; box-shadow: 0 2px 10px rgba(0,0,0,.08); padding: 2rem; font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.15; }
    .sop-meta { margin-bottom: 1rem; color: #4a4a4a; }
    .sop-actions { display:flex; flex-wrap:wrap; justify-content: center; gap:.75rem; margin: 1rem 0 1.5rem; }
    .sop-actions a { border: 0; }
    .draft-banner { background:#fff4d6; border:1px solid #e5c878; border-left:6px solid #c99700; border-radius:4px; padding:1rem; margin:0 0 1rem; }
    .draft-banner p { margin:.25rem 0; }
    .sop-body h2.chapter { margin-top:2rem; border-top:2px solid #ddd; padding-top:1rem; }
    .sop-body h3 { margin-top:1.35rem; }
    .sop-body p, .sop-body li { color:#222; margin: 0 0 12pt 0; }
    .ar2550-note { margin: 0 0 12pt; padding: .75rem; background: #f4f7fb; border-left: 4px solid #0065a4; }
    .sop-start-divider { border: none; border-top: 3px solid #000; margin: 2rem 0 1.25rem; }
    .cover-block { margin: 0 0 1.75rem; }
    .cover-block p { margin: 0 0 0.65rem; }
    .cover-center { text-align: center; }
    .cover-right { text-align: right; }
    .cover-left { text-align: left; }
    .back-to-top-float {
      position: fixed;
      right: 1rem;
      bottom: 1rem;
      z-index: 1000;
      display: inline-block;
      padding: 0.8rem 1rem;
      border-radius: 4px;
    }
    header h1 .site-doc-title-dynamic {
      font-size: 1.1rem;
      font-weight: normal;
    }
    @media (max-width: 768px) { .sop-shell { padding: 1rem; } header h1 .site-doc-title-dynamic { font-size: 1rem; } }
    @media print {
      @page { size: auto; margin: 0; }
      html, body { margin: 0 !important; padding: 0 !important; }
      body { background:#fff !important; padding: 1in !important; }
      header, nav, footer, .sop-actions { display:none !important; }
      main { max-width:none; margin:0; padding:0; box-shadow:none; min-height:auto; }
      .sop-shell { border:none; box-shadow:none; padding:0; max-width:none; margin: 0 !important; }
      .draft-banner { display:none !important; }
      a[href]:after { content: ""; }
      html, body, .sop-shell * { color:#000 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      h1, h2, h3, h4, p, li, strong { color:#000 !important; }
      .sop-start-divider { border-top-color: #000 !important; }
      .back-to-top-float { display: none !important; }
      .sop-body h2.chapter, .sop-body h3 { break-after: avoid; }
      .sop-body p, .sop-body li { orphans:3; widows:3; }
    }
  </style>
</head>
<body id="page-top">
  <header><h1>CMDP Compliance Document: <span id="site-compliance-doc-badge" class="site-doc-title-dynamic" aria-live="polite"></span></h1></header>
  <nav data-site-nav data-root-path="../" aria-label="Main navigation"></nav>
  <main>
    <section class="sop-shell">
"""

DRAFT_BANNER_AND_ACTIONS = """      <!-- DRAFT BLOCK START: remove this section when approved -->
      <section id="draft-banner" class="draft-banner">
        <h2>Draft Notice</h2>
        <p><strong>Status:</strong> Draft for review and coordination.</p>
        <p>Delete this entire block on approval to publish as final.</p>
      </section>

      <div class="sop-actions">
        <a class="download-btn" href="../assets/word/sops/10.10.1-sop-driver-training.docx" download="10.10.1-sop-driver-training.docx">Download Word (AR&nbsp;25-50)</a>
      </div>
      <hr class="sop-start-divider" />
"""

HTML_SHELL_TAIL = """
      <hr class="sop-start-divider" />
      <div class="sop-actions" aria-label="End of document downloads">
        <a class="download-btn" href="../assets/word/sops/10.10.1-sop-driver-training.docx" download="10.10.1-sop-driver-training.docx">Download Word (AR&nbsp;25-50)</a>
      </div>
    </section>
  </main>
  <a class="download-btn back-to-top-float" href="#page-top" aria-label="Back to top">Back to Top</a>
  <footer><p>CMDP Compliance Documentation - FY24-25</p></footer>
  <script>
    document.addEventListener("DOMContentLoaded", function () {
      var src = document.getElementById("sop-cover-title-short");
      var dst = document.getElementById("site-compliance-doc-badge");
      if (!src || !dst) return;
      dst.textContent = src.textContent.replace(/\\s+/g, " ").trim();
    });
  </script>
  <script src="../static/scripts/site-nav.js"></script>
</body>
</html>
"""


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def bold(s: str) -> str:
    s = html.unescape(s)
    s = esc(s)
    parts: list[str] = []
    i = 0
    while True:
        j = s.find("**", i)
        if j == -1:
            parts.append(s[i:])
            break
        parts.append(s[i:j])
        k = s.find("**", j + 2)
        if k == -1:
            parts.append(s[j:])
            break
        parts.append("<strong>" + s[j + 2 : k] + "</strong>")
        i = k + 2
    return "".join(parts)


def normalize_physical_line(raw: str) -> str:
    s = raw.replace("\ufeff", "").rstrip("\r")
    stripped = s.lstrip()
    ws_prefix = s[: len(s) - len(stripped)]
    core = stripped
    while core.startswith("\\"):
        if core.startswith("\\---"):
            core = core[1:]
            continue
        rest = core[1:]
        if (
            rest.startswith("#")
            or rest.startswith("- ")
            or rest.startswith("-	")
            or rest.startswith("[")
        ):
            core = core[1:]
            continue
        break
    return ws_prefix + core


def decode_md(raw_bytes: bytes) -> str:
    if raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff"):
        return raw_bytes.decode("utf-16")
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        return raw_bytes.decode("utf-8-sig")
    sample = raw_bytes[: min(512, len(raw_bytes))]
    if len(sample) >= 8:
        odd_indices = range(1, len(sample), 2)
        odd_nulls = sum(1 for j in odd_indices if sample[j] == 0)
        odd_count = len(list(odd_indices))
        if odd_count >= 4 and odd_nulls >= odd_count * 0.85:
            return raw_bytes.decode("utf-16-le")
    return raw_bytes.decode("utf-8")


def unescape_inline_brackets(s: str) -> str:
    return re.sub(r"\\([\[\]])", r"\1", s)


def load_lines(md_path: Path) -> list[str]:
    raw = decode_md(md_path.read_bytes()).splitlines()
    return [
        normalize_physical_line(unescape_inline_brackets(line)) for line in raw
    ]


def is_wiki(ln: str) -> bool:
    t = ln.strip()
    if "[[" in t and "]]" in t:
        return True
    if "sops.index" in t and "|" in t:
        return True
    return False


def merged_paragraphs(block: list[str]) -> list[str]:
    paras: list[str] = []
    bucket: list[str] = []
    for ln in block:
        t = ln.strip()
        if not t:
            if bucket:
                paras.append(" ".join(bucket))
                bucket = []
            continue
        bucket.append(t)
    if bucket:
        paras.append(" ".join(bucket))
    return paras


def find_summary_heading(lines: list[str]) -> int:
    for i, ln in enumerate(lines):
        if is_wiki(ln):
            continue
        ts = ln.strip()
        if ts.startswith("# ") and ts[2:].strip().upper().startswith("SUMMARY"):
            return i
    raise SystemExit("Markdown must contain a '# SUMMARY of CHANGE' heading.")


def consume_blank_and_rules(i: int, lines: list[str]) -> int:
    n = len(lines)
    while i < n:
        ts = lines[i].strip()
        if is_wiki(lines[i]):
            i += 1
            continue
        if not ts or ts == "---":
            i += 1
            continue
        break
    return i


def consume_cover(lines: list[str], end_exclusive: int) -> tuple[list[str], str, str]:
    """Return HTML fragments inside cover-block, plus (long_title, short_title_hint)."""
    parts: list[str] = []

    long_title = "DRIVER TRAINING STANDARD OPERATING PROCEDURE"
    short_title_hint = "176TH EN BDE DRIVER TRAINING SOP"

    i = consume_blank_and_rules(0, lines)
    addr_buf: list[str] = []

    def flush_addr() -> None:
        nonlocal addr_buf
        if not addr_buf:
            return
        addr_paras = merged_paragraphs(addr_buf)
        if addr_paras:
            if len(addr_paras) <= 8 and len(max(addr_paras, key=len)) < 260:
                for ptxt in addr_paras:
                    parts.append(f'<p class="cover-left">{bold(ptxt)}</p>')
            else:
                merged_block = bold(" ".join(addr_paras))
                parts.append(f'<p class="cover-left">{merged_block}</p>')
        addr_buf = []

    while i < end_exclusive:
        ts = lines[i].strip()
        if is_wiki(lines[i]):
            i += 1
            continue
        if not ts:
            addr_buf.append("")
            i += 1
            continue

        # Horizontal rules omitted from MIL writing style; tolerate any remaining "---" noise.
        if ts == "---":
            flush_addr()
            i += 1
            continue

        # Markdown headings terminate address accumulation (no hr required).
        if ts.startswith("# ") or ts.startswith("## "):
            flush_addr()

        # Headings ending cover narrative
        if ts.startswith("# "):
            h = ts[2:].strip()
            hu = h.upper()
            if hu.startswith("DRAFT"):
                parts.append(f'<p class="cover-right">{bold(h)}</p>')
                i += 1
                continue
            if "STANDARD OPERATING PROCEDURES" in hu or hu.startswith(
                ("176TH", "MAINTENANCE", "GROUND")
            ):
                long_title = h
                parts.append(f'<p class="cover-center">{bold(h)}</p>')
                i += 1
                i = consume_blank_and_rules(i, lines)
                short_line_for_span = short_title_hint
                if i < end_exclusive and lines[i].strip().startswith("## "):
                    short_line_for_span = lines[i].strip()[3:].strip()
                    short_title_hint = short_line_for_span
                    i += 1
                i = consume_blank_and_rules(i, lines)
                by_ord = ""
                if i < end_exclusive:
                    cand = lines[i].strip()
                    if cand.upper().startswith("BY ORDER OF THE COMMANDER"):
                        by_ord = cand
                        i += 1
                span_txt = bold(short_line_for_span) if short_line_for_span.strip() else ""
                span = f'<span id="sop-cover-title-short">{span_txt}</span>'
                if by_ord and span_txt:
                    parts.append(f'<p class="cover-center">{span}<br/>{bold(by_ord)}</p>')
                elif span_txt:
                    parts.append(f'<p class="cover-center">{span}</p>')
                elif by_ord:
                    parts.append(f'<p class="cover-center">{bold(by_ord)}</p>')
                continue

        if ts.startswith("## ") and ts[3:].strip().upper().startswith("OFFICIAL"):
            i += 1
            blk: list[str] = []
            while i < end_exclusive:
                u = lines[i].strip()
                if is_wiki(lines[i]):
                    i += 1
                    continue
                if not u:
                    blk.append("")
                    i += 1
                    continue
                if u == "---":
                    i += 1
                    continue
                if u.startswith(("## ", "# ")):
                    break
                blk.append(lines[i].strip())
                i += 1
            paras = merged_paragraphs(blk)
            inner = bold("OFFICIAL:") + "<br/>" + "<br/>".join(bold(p) for p in paras)
            parts.append(f'<p class="cover-right">{inner}</p>')
            continue

        if ts.startswith("## "):
            raw_lbl = ts[3:].strip()
            label = raw_lbl.rstrip(":")
            lbl_plain = esc(label.strip().rstrip("."))
            lbl_key = lbl_plain + ":"
            i += 1
            blk: list[str] = []
            while i < end_exclusive:
                u = lines[i].strip()
                if is_wiki(lines[i]):
                    i += 1
                    continue
                if not u:
                    blk.append("")
                    i += 1
                    continue
                if u == "---":
                    i += 1
                    continue
                if u.startswith("## ") or u.startswith("# "):
                    break
                blk.append(lines[i])
                i += 1
            lbl_lower = label.lower()
            paras = merged_paragraphs([x.strip() for x in blk])
            if lbl_lower.startswith("distribution"):
                parts.append(f"<p class=\"cover-left\"><strong>{lbl_key}</strong></p>")
                for ptxt in paras:
                    if ptxt.upper() == "A":
                        parts.append('<p class="cover-center">A</p>')
                    else:
                        parts.append(f'<p class="cover-left">{bold(ptxt)}</p>')
                peek = consume_blank_and_rules(i, lines)
                while peek < end_exclusive and lines[peek].strip().upper() == "A":
                    parts.append('<p class="cover-center">A</p>')
                    peek += 1
                    peek = consume_blank_and_rules(peek, lines)
                i = peek
            else:
                body_txt = paras[0] if paras else ""
                if body_txt:
                    parts.append(
                        f'<p class="cover-left"><strong>{lbl_key}</strong> {bold(body_txt)}</p>'
                    )
                else:
                    parts.append(f'<p class="cover-left"><strong>{lbl_key}</strong></p>')
            continue

        addr_buf.append(lines[i])
        i += 1

    flush_addr()
    return parts, long_title, short_title_hint


def render_body(lines: list[str], start_idx: int) -> str:
    out: list[str] = []
    i = consume_blank_and_rules(start_idx, lines)
    list_stack = 0
    first_after_chapter = False

    n = len(lines)

    while i < n:
        if is_wiki(lines[i]):
            i += 1
            continue
        ts = lines[i].strip()
        if not ts:
            i += 1
            continue

        if ts == "---":
            while list_stack:
                out.append("</ul>")
                list_stack -= 1
            i += 1
            continue

        if ts.startswith("|") and ts.endswith("|"):
            while list_stack:
                out.append("</ul>")
                list_stack -= 1
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                row = [
                    c.strip()
                    for c in lines[i].strip().strip("|").split("|")
                ]
                if all(re.fullmatch(r"-+", cell.replace(" ", "").replace(":", "")) for cell in row):
                    i += 1
                    continue
                rows.append(row)
                i += 1
            if rows:
                out.append("<table>")
                out.append("<thead><tr>")
                for c in rows[0]:
                    out.append(f"<th>{bold(c)}</th>")
                out.append("</tr></thead>")
                if len(rows) > 1:
                    out.append("<tbody>")
                    for r in rows[1:]:
                        out.append("<tr>")
                        for c in r:
                            out.append(f"<td>{bold(c)}</td>")
                        out.append("</tr>")
                    out.append("</tbody>")
                out.append("</table>")
            continue

        if ts.startswith("# ") and not ts.startswith("##"):
            inner = ts[2:].strip()
            while list_stack:
                out.append("</ul>")
                list_stack -= 1
            hu = inner.upper()

            chapter_match = hu.startswith("CHAPTER ")
            enumerated_chapter = re.match(r"^\d+\.\s+[A-Z]", inner)
            summary_head = hu.startswith("SUMMARY")

            if summary_head:
                out.append(f"<h2>{bold(inner)}</h2>")
                first_after_chapter = False
                i += 1
                continue

            if chapter_match or enumerated_chapter:
                out.append(f'<h2 class="chapter">{bold(inner)}</h2>')
                first_after_chapter = True
                i += 1
                continue

            out.append(f"<h2>{bold(inner)}</h2>")
            first_after_chapter = False
            i += 1
            continue

        if "**CMDP" in ts.upper() or ts.upper().startswith("CMDP REFERENCE"):
            while list_stack:
                out.append("</ul>")
                list_stack -= 1
            out.append(f"<p>{bold(ts)}</p>")
            i += 1
            continue

        if "**APPROVAL" in ts:
            while list_stack:
                out.append("</ul>")
                list_stack -= 1
            out.append("<hr />")
            out.append(f"<p>{bold(ts)}</p>")
            i += 1
            continue

        if ts.startswith("## ") and not ts.startswith("###"):
            subt = ts[3:].strip()

            while list_stack:
                out.append("</ul>")
                list_stack -= 1

            if SECTION_RE.match(subt):
                if first_after_chapter:
                    out.append(f"<h2>{bold(subt)}</h2>")
                    first_after_chapter = False
                else:
                    out.append(f"<h3>{bold(subt)}</h3>")
            else:
                out.append(f"<h2>{bold(subt)}</h2>")
                first_after_chapter = False
            i += 1
            continue

        if ts.startswith("- "):
            if list_stack == 0:
                out.append("<ul>")
                list_stack = 1
            item = ts[2:].strip()
            out.append(f"<li>{bold(item)}</li>")
            i += 1
            continue

        while list_stack:
            out.append("</ul>")
            list_stack -= 1

        bucket = [ts]
        i += 1
        while i < n:
            nx = lines[i].strip()
            if is_wiki(lines[i]):
                i += 1
                continue
            if not nx:
                break
            if nx == "---":
                break
            if lines[i].strip().startswith("#"):
                break
            if nx.startswith("|"):
                break
            if nx.startswith("- "):
                break
            if nx.startswith("## "):
                break
            bucket.append(nx)
            i += 1
        out.append(f"<p>{bold(' '.join(bucket))}</p>")

    while list_stack:
        out.append("</ul>")
        list_stack -= 1

    return "\n".join(out)


def write_fixed_markdown(lines: list[str], dest: Path) -> None:
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    fix_md = "--fix-md" in sys.argv
    lines = load_lines(MD_SRC)
    if fix_md:
        write_fixed_markdown(lines, MD_SRC)
        print(f"Normalized escapes in {MD_SRC.relative_to(REPO)}")

    summary_i = find_summary_heading(lines)
    cover_lines = lines[:summary_i]
    cover_parts, _long_t, _short_t = consume_cover(cover_lines, len(cover_lines))

    body_html = render_body(lines, summary_i)

    inner = (
        DRAFT_BANNER_AND_ACTIONS
        + '      <article class="sop-body">\n'
        + '        <div class="cover-block">\n'
        + "\n".join(f"          {p}" for p in cover_parts)
        + "\n        </div>\n"
        + body_html
        + "\n      </article>\n"
        + HTML_SHELL_TAIL
    )

    full = HTML_SHELL_HEAD + inner
    HTML_OUT.write_text(full, encoding="utf-8", newline="\n")
    print(f"Wrote {HTML_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
