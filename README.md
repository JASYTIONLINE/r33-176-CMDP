# CMDP Compliance Documentation Website

This repository contains a static HTML website for CMDP (Command Maintenance Discipline Program) compliance documentation.

1. The website is hosted on GitHub Pages.
2. The site is built with static HTML files - no build process required.
3. The website automatically updates when you push changes to GitHub.

> [!NOTE]
> This is a static HTML website. All HTML files are in the root directory and subdirectories (`memos/`, `sops/`).

## Website Structure

- `index.html` - Main landing page
- `memos/` - Memorandum HTML pages
- `sops/` - Standard Operating Procedure HTML pages
- `content/word/` - Word document templates
- `css/` - Stylesheets

## Development 

### Editing HTML Files

Edit HTML files directly in the repository:
- `index.html` - Main page
- `memos/*.html` - Individual memo pages
- `sops/*.html` - Individual SOP pages

### Adding New Pages

1. Create a new HTML file in the appropriate directory (`memos/` or `sops/`)
2. Follow the existing HTML structure and navigation pattern
3. Commit and push to GitHub
4. The site will automatically deploy via GitHub Actions

### Word Document Templates

Word document templates are stored in `content/word/`:
- `word-memo/` - Memorandum templates
- `word-sop/` - SOP templates

<p>&nbsp;</p>

---

## Important Notes

- This is a **static HTML website** - no build process required
- HTML files are served directly from the repository root
- GitHub Actions automatically deploys changes to GitHub Pages
- Word document templates are stored in `content/word/` for download

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). 

---

## License

This template is licensed under the [MIT License](https://opensource.org/licenses/MIT).
