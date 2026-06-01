"""Convert sops/pubs.md to sops/10.18.1-sop-publications.html (authoritative markdown source)."""
from __future__ import annotations

import re
from pathlib import Path

from scripts.paths import sop_md_dir, sop_publish_dir

_MD = sop_md_dir()
_PUB = sop_publish_dir()

MD_PATH = _MD / "pubs.md"
OUT_FRAG = _PUB / "_pubs_body.frag.html"
OUT_PAGE = _PUB / "10.18.1-sop-publications.html"

BRIGADE_DISPLAY = "176th Engineer Brigade (TXARNG)"

ADMIN_HTML = """<h2>Administrative Data</h2>
<table>
<thead><tr><th>Field</th><th>Value</th></tr></thead>
<tbody>
<tr><td><strong>Effective Date</strong></td><td>[DD MONTH YYYY]</td></tr>
<tr><td><strong>Supersedes</strong></td><td>[Previous SOP Date or N/A]</td></tr>
<tr><td><strong>Review Date</strong></td><td>[Annual Review Date]</td></tr>
<tr><td><strong>Approval Authority</strong></td><td>[Commander Name, Rank]</td></tr>
</tbody>
</table>
<hr>
"""

APPROVAL_HTML = """<hr>
<p><strong>APPROVAL:</strong></p>
<p><strong>[LAST NAME, FIRST NAME MI.]</strong></p>
<p>[RANK, BRANCH, COMPONENT]</p>
<p>Commanding</p>
<hr>
<p><strong>CMDP Reference:</strong> 10(18)-1</p>
"""

SOP_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PUBLICATIONS STANDARD OPERATING PROCEDURE - CMDP Compliance</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>CMDP Compliance Documents</h1>
    </header>
    <nav data-site-nav data-root-path="../" aria-label="Main navigation"></nav>
    <main>
{body}
    </main>
    <footer>
        <p>CMDP Compliance Documentation - FY24-25</p>
    </footer>
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
    s = esc(s)
    out: list[str] = []
    i = 0
    while True:
        j = s.find("**", i)
        if j == -1:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k = s.find("**", j + 2)
        if k == -1:
            out.append(s[j:])
            break
        out.append("<strong>" + s[j + 2 : k] + "</strong>")
        i = k + 2
    return "".join(out)


LINK_PAT = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def format_inline(text: str) -> str:
    """Apply **bold** and Markdown [label](https://...) links (https/http only)."""
    parts: list[str] = []
    pos = 0
    for m in LINK_PAT.finditer(text):
        parts.append(bold(text[pos : m.start()]))
        label = m.group(1)
        url = m.group(2).strip()
        if url.startswith("https://") or url.startswith("http://"):
            parts.append(
                f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{bold(label)}</a>'
            )
        else:
            parts.append(bold(text[m.start() : m.end()]))
        pos = m.end()
    parts.append(bold(text[pos:]))
    return "".join(parts)


def decode_md(raw_bytes: bytes) -> str:
    if raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff"):
        return raw_bytes.decode("utf-16")
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        return raw_bytes.decode("utf-8-sig")
    if (
        len(raw_bytes) >= 4
        and raw_bytes[0] == ord("#")
        and raw_bytes[1] == 0
        and raw_bytes[3] == 0
    ):
        return raw_bytes.decode("utf-16-le")
    sample = raw_bytes[: min(512, len(raw_bytes))]
    if len(sample) >= 8:
        odd_indices = range(1, len(sample), 2)
        odd_nulls = sum(1 for j in odd_indices if sample[j] == 0)
        odd_count = len(list(odd_indices))
        if odd_count >= 4 and odd_nulls >= odd_count * 0.85:
            return raw_bytes.decode("utf-16-le")
    return raw_bytes.decode("utf-8")


def strip_banner_and_cover(lines: list[str]) -> list[str]:
    """Drop blockquote banner, document title, brigade line, and leading ---."""
    i = 0
    while i < len(lines) and lines[i].strip().startswith(">"):
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].strip() == "---":
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# PUBLICATIONS STANDARD"):
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().startswith("**"):
        i += 1
    while i < len(lines) and lines[i].strip() == "---":
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].strip() == "---":
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return lines[i:]


def md_lines_to_html(lines: list[str]) -> str:
    html: list[str] = []
    i = 0
    list_stack: list[str] = []
    ol_open = False

    def close_ul():
        nonlocal list_stack
        while list_stack:
            html.append("</ul>")
            list_stack.pop()

    def close_ol():
        nonlocal ol_open
        if ol_open:
            html.append("</ol>")
            ol_open = False

    def close_lists():
        close_ul()
        close_ol()

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        if stripped == "---":
            close_lists()
            html.append("<hr>")
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                sep = all(re.fullmatch(r"-+", c.replace(" ", "")) for c in row)
                if not sep:
                    rows.append(row)
                i += 1
            if rows:
                html.append("<table>")
                html.append("<thead><tr>")
                for c in rows[0]:
                    html.append(f"<th>{format_inline(c)}</th>")
                html.append("</tr></thead>")
                if len(rows) > 1:
                    html.append("<tbody>")
                    for r in rows[1:]:
                        html.append("<tr>")
                        for c in r:
                            html.append(f"<td>{format_inline(c)}</td>")
                        html.append("</tr>")
                    html.append("</tbody>")
                html.append("</table>")
            continue

        num_m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if num_m:
            close_ul()
            if not ol_open:
                html.append("<ol>")
                ol_open = True
            html.append(f"<li>{format_inline(num_m.group(2))}</li>")
            i += 1
            continue
        close_ol()

        if ln.startswith("# ") and not ln.startswith("##"):
            close_lists()
            t = ln[2:].strip()
            html.append(f"<h2>{bold(t)}</h2>")
            i += 1
            continue

        if ln.startswith("## ") and not ln.startswith("###"):
            close_lists()
            t = ln[3:].strip()
            if t == "Administrative Data":
                html.append(f"<h2>{bold(t)}</h2>")
            else:
                html.append(f"<h3>{bold(t)}</h3>")
            i += 1
            continue

        if ln.startswith("### "):
            close_lists()
            t = ln[4:].strip()
            html.append(f"<h4>{bold(t)}</h4>")
            i += 1
            continue

        if stripped.startswith("- "):
            close_ol()
            if not list_stack:
                html.append("<ul>")
                list_stack.append("ul")
            item = stripped[2:].strip()
            html.append(f"<li>{format_inline(item)}</li>")
            i += 1
            continue

        close_lists()
        paras = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if nxt == "---":
                break
            if lines[i].startswith("#"):
                break
            if lines[i].startswith("|"):
                break
            if nxt.startswith("- "):
                break
            if re.match(r"^\d+\.\s+", nxt):
                break
            paras.append(nxt)
            i += 1
        body = " ".join(paras)
        html.append(f"<p>{format_inline(body)}</p>")
        continue

    close_lists()
    return "\n".join(html)


def main() -> None:
    raw_bytes = MD_PATH.read_bytes()
    text = decode_md(raw_bytes)
    raw_lines = text.splitlines()
    filtered: list[str] = []
    for ln in raw_lines:
        if "[[" in ln and "]]" in ln:
            continue
        filtered.append(ln)
    while filtered and (filtered[-1].strip() == "" or "[[" in filtered[-1]):
        filtered.pop()

    body_lines = strip_banner_and_cover(filtered)
    body_inner = md_lines_to_html(body_lines)

    header_html = f"""<hr>
<h1>PUBLICATIONS STANDARD OPERATING PROCEDURE</h1>
<p><strong>{esc(BRIGADE_DISPLAY)}</strong></p>
<hr>
{ADMIN_HTML}"""

    body_text = header_html + body_inner + "\n" + APPROVAL_HTML
    OUT_FRAG.write_text(body_inner + "\n", encoding="utf-8")
    page_html = SOP_SHELL.format(body=body_text)
    with OUT_PAGE.open("w", encoding="utf-8", newline="\r\n") as f:
        f.write(page_html)
    print(f"Wrote {OUT_FRAG} and {OUT_PAGE} ({len(body_inner)} chars inner body)")


if __name__ == "__main__":
    main()
