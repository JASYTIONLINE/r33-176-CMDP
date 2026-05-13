"""Convert sops/drivetrain.md to HTML (reference-only draft MD; discard after the new SOP source replaces this workflow)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "drivetrain.md"
OUT_FRAG = ROOT / "_driver_training_body.frag.html"
OUT_PAGE = ROOT / "101.10.1-sop-driver-training.html"

SOP_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DRIVER TRAINING STANDARD OPERATING PROCEDURE - CMDP Compliance</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>CMDP Compliance Documents</h1>
    </header>
    <nav data-site-nav data-root-path="../" aria-label="Main navigation"></nav>
    <main>{body}
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


def decode_md(raw_bytes: bytes) -> str:
    if raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff"):
        return raw_bytes.decode("utf-16")
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        return raw_bytes.decode("utf-8-sig")
    # UTF-16 LE without BOM often begins "#\x00" or BOM-less UTF-16 text editors save this way
    if (
        len(raw_bytes) >= 4
        and raw_bytes[0] == ord("#")
        and raw_bytes[1] == 0
        and raw_bytes[3] == 0
    ):
        return raw_bytes.decode("utf-16-le")
    # UTF-16 LE without BOM starting with other Markdown (e.g. blockquote ">"): nulls on odd indices
    sample = raw_bytes[: min(512, len(raw_bytes))]
    if len(sample) >= 8:
        odd_indices = range(1, len(sample), 2)
        odd_nulls = sum(1 for j in odd_indices if sample[j] == 0)
        odd_count = len(list(odd_indices))
        if odd_count >= 4 and odd_nulls >= odd_count * 0.85:
            return raw_bytes.decode("utf-16-le")
    return raw_bytes.decode("utf-8")


def main() -> None:
    raw_bytes = MD_PATH.read_bytes()
    text = decode_md(raw_bytes)
    raw_lines = text.splitlines()
    lines: list[str] = []
    started = False
    for ln in raw_lines:
        if "[[" in ln and "]]" in ln:
            continue
        if not started:
            if ln.startswith("# DRIVER TRAINING"):
                started = True
                lines.append(ln)
            continue
        lines.append(ln)

    # Drop trailing wiki/backlink lines
    while lines and (lines[-1].strip() == "" or "[[" in lines[-1]):
        lines.pop()

    html: list[str] = []
    i = 0
    list_stack: list[str] = []
    seen_main_h1 = False

    def close_list():
        nonlocal list_stack
        while list_stack:
            html.append("</ul>")
            list_stack.pop()

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        if stripped == "---":
            close_list()
            html.append("<hr>")
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # Markdown table
        if stripped.startswith("|") and stripped.endswith("|"):
            close_list()
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
                    html.append(f"<th>{bold(c)}</th>")
                html.append("</tr></thead>")
                if len(rows) > 1:
                    html.append("<tbody>")
                    for r in rows[1:]:
                        html.append("<tr>")
                        for c in r:
                            html.append(f"<td>{bold(c)}</td>")
                        html.append("</tr>")
                    html.append("</tbody>")
                html.append("</table>")
            continue

        if ln.startswith("# ") and not ln.startswith("##"):
            close_list()
            t = ln[2:].strip()
            if not seen_main_h1 and t.upper().startswith("DRIVER TRAINING"):
                html.append(f"<h1>{bold(t)}</h1>")
                seen_main_h1 = True
            else:
                html.append(f"<h2>{bold(t)}</h2>")
            i += 1
            continue

        if ln.startswith("## ") and not ln.startswith("###"):
            close_list()
            t = ln[3:].strip()
            # Match CMDP SOP shell: Administrative Data is h2; other ## subsections are h3
            if t == "Administrative Data":
                html.append(f"<h2>{bold(t)}</h2>")
            else:
                html.append(f"<h3>{bold(t)}</h3>")
            i += 1
            continue

        if ln.startswith("### "):
            close_list()
            t = ln[4:].strip()
            html.append(f"<h4>{bold(t)}</h4>")
            i += 1
            continue

        if stripped.startswith("- "):
            if not list_stack:
                html.append("<ul>")
                list_stack.append("ul")
            item = stripped[2:].strip()
            html.append(f"<li>{bold(item)}</li>")
            i += 1
            continue

        # Plain paragraph (preserve line as single block; merge continuation without bullet?)
        close_list()
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
            paras.append(nxt)
            i += 1
        body = " ".join(paras)
        html.append(f"<p>{bold(body)}</p>")
        continue

    close_list()
    body_text = "\n".join(html)
    OUT_FRAG.write_text(body_text + "\n", encoding="utf-8")
    page_body = "\n\n<hr>\n\n" + body_text.strip()
    page_html = SOP_SHELL.format(body=page_body)
    with OUT_PAGE.open("w", encoding="utf-8", newline="\r\n") as f:
        f.write(page_html)
    print(f"Wrote {OUT_FRAG} and {OUT_PAGE} ({len(body_text)} chars body)")


if __name__ == "__main__":
    main()
