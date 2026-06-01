# Contributing to the CMDP site

Read [`assets/docs/REPO_LAYOUT.md`](assets/docs/REPO_LAYOUT.md) first for how **`source/`** (authoring) differs from **`memos/`** and **`sops/`** (published HTML).

## Main site (`index.html`)

The home page is **hand-maintained** in the repo root as [`index.html`](index.html). To drive it from Markdown instead, add [`source/cmdp-index.md`](source/cmdp-index.md); `python -m scripts.site.build_html_site` will then regenerate `index.html` from that file. The file [`source/index.md`](source/index.md) is only a **readme** for the `source/` tree, not the public index.

## Memos (Markdown → HTML)

1. Edit the memo under [`source/memos/`](source/memos/) (`.md`).
2. From the **repository root**, run:
   ```bash
   python -m scripts.site.build_html_site
   ```
3. Commit both the Markdown change and the regenerated file under [`memos/`](memos/) (`.html`).
4. Confirm the Word template exists under [`assets/word/memos/`](assets/word/memos/) if the page offers a download.

## SOPs (Markdown → HTML / DOCX)

- Bulk DOCX from SOP Markdown:
  ```bash
  python -m scripts.word.convert_sops_to_docx
  ```
  Output: [`assets/word/sops/`](assets/word/sops/).
- Specialized SOP generators live under [`scripts/sops/`](scripts/sops/); see [`scripts/README.md`](scripts/README.md).

## ESR class

- Maintain the published slide deck under [`content/HTML/esr-class/`](content/HTML/esr-class/).
- Deployed URL path remains **`/content/esr-class/...`** (CI copies that tree into `_site/content/esr-class`).

## Conventions

- Run Python tools from the repo root unless a script’s docstring says otherwise.
- Prefer small, focused commits (source + generated HTML together when you run the builder).
- Do not commit gitignored local draft outputs (e.g. `drafts/` per [.gitignore](.gitignore) if used).
