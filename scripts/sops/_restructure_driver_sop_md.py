"""Rewrite driver training SOP markdown to match maint SOP structure.

Run from repo root:  python -m scripts.sops._restructure_driver_sop_md

Rewrites source/sops/10.10.1-sop-driver-training.md in place.
"""
from __future__ import annotations

import re
from pathlib import Path

from scripts.paths import repo_root

_REPO = repo_root()
MD = _REPO / "source/sops/10.10.1-sop-driver-training.md"


def _find(lines: list[str], pattern: str, start: int = 0) -> int:
    rx = re.compile(pattern)
    for i in range(start, len(lines)):
        if rx.search(lines[i].strip()):
            return i
    raise ValueError(f"Pattern not found: {pattern}")


def _join_lines(lines: list[str]) -> str:
    return "\n".join(lines) + ("\n" if lines else "")


def _strip_headings_block(lines: list[str]) -> list[str]:
    """Remove leading # Chapter … line if present (already handled)."""
    out = list(lines)
    while out and not out[0].strip():
        out.pop(0)
    if out and re.match(r"^# Chapter\b", out[0].strip()):
        out = out[1:]
        while out and not out[0].strip():
            out.pop(0)
    return out


def _retitle_subsections(lines: list[str], old_major: int, new_major: int) -> list[str]:
    pat = re.compile(rf"^## {old_major}-(\d+)\.\s*(.*)$")
    out: list[str] = []
    for ln in lines:
        m = pat.match(ln.strip())
        if m:
            out.append(f"### {new_major}.{m.group(1)} {m.group(2)}")
        else:
            out.append(ln)
    return out


def _chapter_heading_to_section(
    line: str, section_num: int, title_override: str | None = None
) -> str:
    if title_override:
        return f"## {section_num}. {title_override}"
    s = line.strip()
    m = re.match(r"^# Chapter \d+\s*[–-]\s*(.+)$", s)
    if m:
        return f"## {section_num}. {m.group(1).strip().upper()}"
    if re.match(r"^#\s*4\.\s*RESPONSIBILITIES\s*$", s, re.I):
        return f"## {section_num}. RESPONSIBILITIES"
    return line


def prep_seg(
    seg: list[str],
    old_maj: int,
    new_maj: int,
    title_override: str | None = None,
) -> str:
    block = list(seg)
    if not block:
        return ""
    if not re.match(
        r"^# (Chapter \d+|4\.\s*RESPONSIBILITIES)", block[0].strip(), re.I
    ):
        raise ValueError(f"Expected chapter heading, got: {block[0]!r}")
    new_head = _chapter_heading_to_section(block[0], new_maj, title_override)
    body = _strip_headings_block(block[1:])
    body = _retitle_subsections(body, old_maj, new_maj)
    return new_head + "\n\n" + _join_lines(body).rstrip() + "\n\n"


def main() -> None:
    lines = MD.read_text(encoding="utf-8").splitlines()

    i_app = _find(lines, r"^##\s+Applicability")
    i_supp = _find(lines, r"^##\s+Supplementation")
    i_sugg = _find(lines, r"^##\s+Suggested Improvements")

    applicability_body = lines[i_app + 1 : i_supp]
    appl = " ".join(s.strip() for s in applicability_body if s.strip())

    supp_body = lines[i_supp + 1 : i_sugg]
    suppl = " ".join(s.strip() for s in supp_body if s.strip())

    i_c1 = _find(lines, r"^# Chapter 1")
    i_c2 = _find(lines, r"^# Chapter 2")
    i_c3 = _find(lines, r"^# Chapter 3")
    i_r4 = _find(lines, r"^#\s*4\.\s*RESPONSIBILITIES")
    i_c5 = _find(lines, r"^# Chapter 5")
    i_c6 = _find(lines, r"^# Chapter 6")
    i_c7 = _find(lines, r"^# Chapter 7")
    i_c8 = _find(lines, r"^# Chapter 8")
    i_c9 = _find(lines, r"^# Chapter 9")
    i_c10 = _find(lines, r"^# Chapter 10")

    i_sum_mark = _find(lines, r"^#\s+SUMMARY of CHANGE")
    i_admin = _find(lines, r"^##\s+Administrative Data")

    i_bul_start = None
    for j in range(i_sum_mark, i_admin):
        t = lines[j].strip()
        if t.startswith("- "):
            i_bul_start = j
            break

    summary_bullets: list[str] = []
    if i_bul_start is not None:
        for j in range(i_bul_start, i_admin):
            if lines[j].strip().startswith("- "):
                summary_bullets.append(lines[j].strip())

    i_approv = _find(lines, r"^\*\*APPROVAL:\*\*")

    seg1 = lines[i_c1:i_c2]
    seg2 = lines[i_c2:i_c3]
    seg3 = lines[i_c3:i_r4]
    seg4 = lines[i_r4:i_c5]
    seg5 = lines[i_c5:i_c6]
    seg6 = lines[i_c6:i_c7]
    seg7 = lines[i_c7:i_c8]
    seg8 = lines[i_c8:i_c9]
    seg9 = lines[i_c9:i_c10]
    seg10 = lines[i_c10:i_approv]

    block1 = list(seg1)
    part1 = "## 1. PURPOSE\n\n" + _join_lines(
        _retitle_subsections(_strip_headings_block(block1[1:]), 1, 1)
    ).rstrip() + "\n\n"

    part2 = (
        "## 2. APPLICABILITY\n\n"
        + appl
        + "\n\n"
        + suppl
        + "\n\n"
        + "---\n\n"
    )

    references_block = (
        "## 3. REFERENCES\n\n"
        "- AR 600-55, The Motor Vehicle Operator and Driver Training Program\n"
        "- AR 385-10, The Army Safety and Occupational Health Program\n"
        "- ATP 5-19, Risk Management\n"
        "- AR 750-1, Army Materiel Maintenance Policy\n"
        "- DA PAM 750-8, Functional Users Manual for the Army Maintenance Management System\n"
        "- Applicable technical manuals (TMs), training circulars (TCs), and operator manuals\n"
        "- Texas Military Department and TXARNG policies, as applicable\n\n"
        "---\n\n"
    )

    p4 = prep_seg(seg2, 2, 4)
    p5 = prep_seg(seg3, 3, 5)
    p6 = prep_seg(seg4, 4, 6)
    p7 = prep_seg(seg5, 5, 7)
    p8 = prep_seg(seg6, 6, 8)
    p9 = prep_seg(seg7, 7, 9)
    p10 = prep_seg(seg8, 8, 10)
    p11 = prep_seg(seg9, 9, 11)
    p12 = prep_seg(seg10, 10, 12)

    summary_section = ""
    if summary_bullets:
        summary_section = (
            "---\n\n## 13. SUMMARY OF ADMINISTRATIVE REVISION\n\n"
            "This administrative revision, dated 14 May 2026:\n\n"
            + "\n".join(summary_bullets)
            + "\n\n"
        )

    middle = (
        part1
        + "---\n\n"
        + part2
        + references_block
        + p4
        + "---\n\n"
        + p5
        + "---\n\n"
        + p6
        + "---\n\n"
        + p7
        + "---\n\n"
        + p8
        + "---\n\n"
        + p9
        + "---\n\n"
        + p10
        + "---\n\n"
        + p11
        + "---\n\n"
        + p12
        + summary_section
    )

    front = (
        "[[sops.index|⬅ Back to SOP Index]]\n\n"
        "---\n\n"
        "# DRIVER TRAINING STANDARD OPERATING PROCEDURE\n\n"
        "**176th Engineer Brigade (TXARNG)**\n\n"
        "---\n\n"
        "## Administrative Data\n\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        "| **Effective Date** | 14 MAY 2026 |\n"
        "| **Supersedes** | N/A |\n"
        "| **Review Date** | 14 MAY 2027 (annual) |\n"
        "| **Approval Authority** | Zebediah E. Miller, COL, TXARNG |\n\n"
        "---\n\n"
    )

    epilogue = "\n".join(lines[i_approv:]) + "\n"

    out = front + middle + epilogue
    out = out.replace("\n------\n", "\n---\n")

    chmap = {10: 12, 9: 11, 8: 10, 7: 9, 6: 8, 5: 7, 4: 6, 3: 5, 2: 4, 1: 1}
    for old in sorted(chmap, reverse=True):
        new = chmap[old]
        out = re.sub(
            rf"\bChapter {old}\b",
            f"section {new}",
            out,
            flags=re.IGNORECASE,
        )
        out = re.sub(rf"\bCHAPTER {old}\b", f"SECTION {new}", out)

    MD.write_text(out, encoding="utf-8", newline="\n")
    print(f"Wrote {MD.relative_to(_REPO)}")


if __name__ == "__main__":
    main()
