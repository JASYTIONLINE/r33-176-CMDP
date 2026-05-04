# CMDP Compliance Documents

This repository hosts the CMDP compliance reference site. The site provides required memorandums, SOPs, downloadable templates, and the Equipment Status Report class.

## Deployment

The site is deployed to GitHub Pages with GitHub Actions. The workflow builds a clean static artifact from the public site files and publishes that artifact to Pages.

Published site inputs:

- `index.html`
- `memos/`
- `sops/`
- `content/esr-class/`
- `assets/`
- `css/`
- `static/`

The deployment does not use Quartz. The repository is organized around static HTML, CSS, JavaScript, and downloadable document assets so memo and SOP pages can be controlled for screen display and print formatting.

## Repository Layout

- `assets/` - Images, PDFs, Word templates, spreadsheets, and other static files.
- `content/` - Source or authored content, including Markdown sources and the ESR class.
- `memos/` - Published memo HTML pages.
- `sops/` - Published SOP HTML pages.
- `css/` - Shared site styles.
- `static/` - Shared site scripts.
- `.github/workflows/ci.yml` - GitHub Pages deployment workflow.

## Editing Guidance

Memo and SOP pages should preserve military document formatting for screen and print output. Formatting should be handled with controlled HTML structure and CSS print rules rather than a wiki or knowledge-base renderer.

Local reference images whose filenames contain `example` are ignored by git and should not be committed.
