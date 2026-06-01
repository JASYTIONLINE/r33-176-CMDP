"""Emit source/sops/10.10.1-sop-driver-training.md from drivetrain.md (UTF-8 wiki mirror)."""
from __future__ import annotations

from pathlib import Path

from scripts.paths import repo_root, resolve_drivetrain_md
from scripts.sops._md_driver_training_to_html import decode_md

MD_PATH = resolve_drivetrain_md()
OUT_PATH = repo_root() / "source" / "sops" / "10.10.1-sop-driver-training.md"


def main() -> None:
    raw_lines = decode_md(MD_PATH.read_bytes()).splitlines()

    i = 0
    if raw_lines and raw_lines[0].startswith("> "):
        while i < len(raw_lines) and raw_lines[i].strip() != "---":
            i += 1
        if i < len(raw_lines) and raw_lines[i].strip() == "---":
            i += 1
        while i < len(raw_lines) and raw_lines[i].strip() == "":
            i += 1

    lines = raw_lines[i:]

    out: list[str] = []
    out.append("[[sops.index|⬅ Back to SOP Index]]")
    out.append("")
    out.append("---")
    out.append("")
    out.append(
        "> **Wiki mirror.** Authoritative draft for the site is **`sops/10.10.1-sop-driver-training.html`**. "
        "`sops/drivetrain.md` is reference-only scaffolding until the rebuilt SOP has a permanent source; "
        "then discard `drivetrain.md` and update this page from that source."
    )
    out.append("")
    out.append("---")
    out.append("")

    for ln in lines:
        if ln.startswith("# ") and not ln.startswith("## "):
            title = ln[2:]
            if title.startswith("DRIVER TRAINING"):
                out.append(ln)
            else:
                out.append("## " + title)
        elif ln.startswith("## ") and not ln.startswith("### "):
            t = ln[3:]
            if t == "Administrative Data":
                out.append(ln)
            else:
                out.append("### " + t)
        else:
            out.append(ln)

    text = "\n".join(out)
    text = text.replace(
        "| Field | Value |\n|---|---|\n| Effective Date |",
        "| Field | Value |\n|-------|-------|\n| **Effective Date** |",
    )
    text = text.replace("| Supersedes |", "| **Supersedes** |")
    text = text.replace("| Review Date |", "| **Review Date** |")
    text = text.replace("| Approval Authority |", "| **Approval Authority** |")

    old_appr = "**APPROVAL:**\n\n**[LAST NAME, FIRST NAME MI.]**"
    new_appr = (
        "**APPROVAL:**\n\n"
        "![Signature](../memos/img/commander-signature.png)\n\n"
        "**[LAST NAME, FIRST NAME MI.]**"
    )
    text = text.replace(old_appr, new_appr)

    text = text.rstrip() + "\n\n---\n\n[[sops.index|⬅ Back to SOP Index]] | [[cmdp-index|Home]]\n"

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_PATH} ({len(text)} chars)")


if __name__ == "__main__":
    main()
