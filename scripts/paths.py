"""Repository root helpers for tooling ( cwd-independent paths )."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (parent of ``scripts``)."""
    return Path(__file__).resolve().parent.parent


def sop_md_dir() -> Path:
    """Canonical authoring directory for numbered SOP markdown."""
    return repo_root() / "source" / "sops"


def sop_publish_dir() -> Path:
    """Directory for published CMDP SOP HTML at the repo root."""
    return repo_root() / "sops"


def resolve_drivetrain_md() -> Path:
    """Locate ``drivetrain.md`` for reference-only pipelines (first match wins)."""
    candidates = (
        sop_md_dir() / "drivetrain.md",
        sop_publish_dir() / "drivetrain.md",
        repo_root() / "content" / "sops" / "drivetrain.md",
    )
    for p in candidates:
        if p.is_file():
            return p
    return candidates[0]
