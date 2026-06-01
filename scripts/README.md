# Tooling (`scripts/`)

All **Python** build utilities live under **`scripts/`** so the repo root stays clean.

Run modules from the **repository root** with `python -m …` so imports resolve correctly (`scripts` must be discoverable — run from `r33-176-CMDP/`, same as cloning and `cd` there).

Shared path helper: **[`paths.py`](paths.py)** exposes `repo_root()`, `sop_md_dir()`, `sop_publish_dir()`, and `resolve_drivetrain_md()` so tools do **not** depend on the current working directory.

## Layout

| Subfolder | Role |
|-----------|------|
| [`site/`](site/) | Memo/SOP Markdown → HTML for the Pages site (`build_html_site`, `convert_md_to_html`). |
| [`word/`](word/) | SOP Markdown → Word (`convert_sops_to_docx`). |
| [`sops/`](sops/) | Specialized SOP HTML/DOCX pipelines (`_md_*_to_html`, driver training, draft banner + masthead hooks). |

## Common commands

| Command | Purpose |
|---------|---------|
| `python -m scripts.site.build_html_site` | Regenerate memo/SOP HTML from Markdown under **`source/`** into **`memos/`** and **`sops/`**. |
| `python -m scripts.word.convert_sops_to_docx` | Bulk SOP Markdown → DOCX → **`assets/word/sops/`** (excluding index/template/pipeline-only stems). |
| `python -m scripts.sops._md_batteries_to_html` | Regenerate **`sops/10.14.3-sop-battery-program.html`** from **`source/sops/batteries.md`**. |
| `python -m scripts.sops._md_cbrn_to_html` | Regenerate **`sops/10.16.2-sop-cbrn.html`**. |
| `python -m scripts.sops._md_hazmat_to_html` | Regenerate **`sops/10.4.3-sop-environmental.html`**. |
| `python -m scripts.sops._md_pubs_to_html` | Regenerate **`sops/10.18.1-sop-publications.html`**. |
| `python -m scripts.sops._md_sko_to_html` | Regenerate **`sops/10.11.1-sop-tool-room.html`**. |
| `python -m scripts.sops._md_arms_room_to_html` | Regenerate **`sops/10.15.1-sop-arms-room.html`**. |
| `python -m scripts.sops._md_driver_training_to_html` | Reference pipeline from **`resolve_drivetrain_md()`** → **`sops/10.10.1-sop-driver-training.html`**. |
| `python -m scripts.sops._emit_driver_training_wiki_md` | Emit **`source/sops/10.10.1-sop-driver-training.md`** from drivetrain. |
| `python -m scripts.sops._build_driver_training_from_content_md` | **`source/sops/10.10.1-…md`** → **`sops/10.10.1-sop-driver-training.html`**. |
| `python -m scripts.sops.build_driver_training_docx_from_md` | Driver-training DOCX (Markdown source). |
| `python -m scripts.sops.build_driver_training_docx_from_html` | Driver-training DOCX (from published HTML). |
| `python -m scripts.sops._build_sopdraft_html` | Draft banner on canonical **`sops/10.*-sop*.html`**, then masthead enhancer. |
| `python -m scripts.sops._enhance_sopdraft_pages` | Masthead / download links (`../assets/word/…`) only. |
| `python -m scripts.sops._restructure_driver_sop_md` | Rewrite driver-training MD structure in place under **`source/sops/`**. |

**Browser assets** (e.g. `static/scripts/site-nav.js`) remain under **`static/`** — that is deployed JavaScript, not this tree.
