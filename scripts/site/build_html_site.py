import re
from pathlib import Path

from scripts.paths import repo_root

_ROOT = repo_root()


# Markdown built by dedicated scripts/sops/_md_* scripts (do not generic-convert).
SOP_PIPELINE_MD_SKIP = frozenset(
    {'batteries.md', 'cbrn.md', 'hazmat.md', 'pubs.md', 'sko.md'},
)


def clean_obsidian_link(link_text):
    """Extract filename from Obsidian link"""
    # Handle [[link|text]] or [[link]]
    match = re.match(r'\[\[([^\]]+)(?:\|([^\]]+))?\]\]', link_text)
    if match:
        link = match.group(1)
        # Remove .md extension and path prefixes
        link = link.replace('.md', '')
        link = link.replace('memos/', '')
        link = link.replace('source/sops/', '')
        link = link.replace('source/memos/', '')
        link = link.replace('content/sops/', '')
        link = link.replace('content/memos/', '')
        # Convert to HTML filename
        if 'sop-' in link:
            link = link.replace('sop-', 'sop-').replace('_', '-')
        link = link.replace('_', '-')
        return link
    return None

def _pipe_table_split_row(line: str) -> list[str]:
    """Split a '|' Markdown table row into cell strings (handles missing trailing '|')."""
    raw = line.strip()
    if not raw:
        return []
    while raw.endswith("|"):
        raw = raw[:-1].rstrip()
    if raw.startswith("|"):
        raw = raw[1:].lstrip()
    parts = raw.split("|")
    return [p.strip() for p in parts]


def _is_markdown_separator_row(parts: list[str]) -> bool:
    if len(parts) < 2:
        return False

    def cell_is_sep(c: str) -> bool:
        t = c.strip()
        if not t:
            return True
        return bool(re.fullmatch(r"[\s\-:]+", t))

    return all(cell_is_sep(c) for c in parts)


def markdown_tables_to_html(md_text: str) -> str:
    """Pipe-style GFM-ish tables → real <table>; output one line each for safe paragraph pass."""
    lines = md_text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and line.count("|") >= 2:
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            parsed: list[list[str]] = []
            for row_ln in block:
                parts = _pipe_table_split_row(row_ln)
                if not parts:
                    continue
                if _is_markdown_separator_row(parts):
                    continue
                parsed.append(parts)
            if not parsed:
                continue
            ncols = max(len(r) for r in parsed)
            rows_html_flat: list[str] = []
            for ri, prow in enumerate(parsed):
                padded = prow + ([""] * (ncols - len(prow)))
                tag = "th" if ri == 0 else "td"
                cells_inner = "".join(
                    f"<{tag}>{_pipe_cell_inline_html(cell)}</{tag}>" for cell in padded
                )
                rows_html_flat.append(f"<tr>{cells_inner}</tr>")
            # Single-line table so downstream line splitter does not fracture tags
            tbl = '<table class="sop-meta-table">' + "".join(rows_html_flat) + "</table>"
            out.append(tbl)
            out.append("")
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


def _escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _pipe_cell_inline_html(cell: str) -> str:
    """Bold **x** only; escape otherwise."""
    if not cell:
        return ""
    parts = re.split(r"(\*\*[^*]+\*\*)", cell)
    chunks: list[str] = []
    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            inner = _escape_html(part[2:-2])
            chunks.append(f"<strong>{inner}</strong>")
        else:
            chunks.append(_escape_html(part))
    return "".join(chunks)


def _markdown_images_to_html(md_text: str) -> str:
    """![alt](url) → <img>; leave http(s) as-is for src."""

    def repl(m: re.Match) -> str:
        alt = _escape_html(m.group(1) or "")
        src = m.group(2).strip()
        return f'<img src="{_escape_html(src)}" alt="{alt}" class="sop-inline-img">'

    return re.sub(r"!\[([^\]]*)\]\(([^\)]+)\)", repl, md_text)


def markdown_to_html_simple(md_text):
    """Convert basic Markdown (SOP authoring) to HTML (tables + images supported)."""
    html = markdown_tables_to_html(md_text)
    html = _markdown_images_to_html(html)
    
    # Convert headers (must do from largest to smallest)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold
    html = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    
    # Convert lists - process line by line
    lines = html.split('\n')
    result = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        stripped = line.strip()
        
        # Unordered list
        if stripped.startswith('- '):
            if not in_ul:
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append('<ul>')
                in_ul = True
            content = stripped[2:].strip()
            # Convert Obsidian links first
            content = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', 
                           lambda m: f'<a href="{get_link_url(m.group(1))}">{m.group(2)}</a>', content)
            content = re.sub(r'\[\[([^\]]+)\]\]', 
                           lambda m: f'<a href="{get_link_url(m.group(1))}">{m.group(1)}</a>', content)
            # Remove any remaining markdown
            content = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', content)
            result.append(f'  <li>{content}</li>')
        # Ordered list
        elif re.match(r'^\d+\.', stripped):
            if not in_ol:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                result.append('<ol>')
                in_ol = True
            content = re.sub(r'^\d+\.\s*', '', stripped)
            # Convert Obsidian links
            content = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', 
                           lambda m: f'<a href="{get_link_url(m.group(1))}">{m.group(2)}</a>', content)
            content = re.sub(r'\[\[([^\]]+)\]\]', 
                           lambda m: f'<a href="{get_link_url(m.group(1))}">{m.group(1)}</a>', content)
            content = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', content)
            result.append(f'  <li>{content}</li>')
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            
            if stripped:
                # Convert Obsidian links first, before wrapping
                line_processed = line
                # Handle [[link|text]] format
                def replace_link_with_text(match):
                    link = match.group(1)
                    text = match.group(2)
                    url = get_link_url(link)
                    return f'<a href="{url}">{text}</a>'
                
                # Handle [[link]] format
                def replace_link(match):
                    link = match.group(1)
                    url = get_link_url(link)
                    # Extract display text (remove path, keep filename)
                    display = link.split('/')[-1].replace('.md', '').replace('-', ' ').title()
                    return f'<a href="{url}">{display}</a>'
                
                line_processed = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', replace_link_with_text, line_processed)
                line_processed = re.sub(r'\[\[([^\]]+)\]\]', replace_link, line_processed)
                
                # Wrap in paragraph if not already a header, raw HTML artifact, or list
                if (
                    stripped.startswith("<table")
                    or stripped.startswith("<img")
                    or stripped.startswith("</table>")
                ):
                    result.append(stripped)
                elif not re.match(r'^<[hH]', stripped) and not stripped.startswith('<ul') and not stripped.startswith('<ol'):
                    if not stripped.startswith('<p>') and not stripped.startswith('<li>'):
                        result.append(f'<p>{line_processed.strip()}</p>')
                    else:
                        result.append(line_processed)
                else:
                    result.append(line_processed)
            else:
                result.append('')
    
    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')
    
    html = '\n'.join(result)
    
    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p><p>', '<p>', html)
    
    return html

def get_link_url(link):
    """Convert Obsidian link to HTML URL"""
    original_link = link
    link = link.replace('.md', '')
    
    # Handle different link formats
    if link.startswith('source/sops/'):
        link = link.replace('source/sops/', 'sops/')
    elif link.startswith('source/memos/'):
        link = link.replace('source/memos/', 'memos/')
    elif link.startswith('content/sops/'):
        link = link.replace('content/sops/', 'sops/')
    elif link.startswith('content/memos/'):
        link = link.replace('content/memos/', 'memos/')
    elif link.startswith('memos/'):
        link = link  # Keep as is
    elif 'sop-' in link or link.startswith('10.') and 'sop' in link:
        # SOP file
        if not link.startswith('sops/'):
            link = 'sops/' + link
    elif link.startswith('10.') or link.startswith('101.'):
        # Memo file - check if it's a memo or SOP
        if 'sop' in link.lower():
            if not link.startswith('sops/'):
                link = 'sops/' + link
        else:
            if not link.startswith('memos/'):
                link = 'memos/' + link
    elif link == 'cmdp-index':
        link = 'index'
    elif link == 'memos.index' or link == 'memos/index':
        link = 'memos/index'
    elif link == 'sops.index' or link == 'sops/index':
        link = 'sops/index'
    
    # Add .html extension if not present and not an external link
    if not link.startswith('http') and not link.endswith('.html') and not link.endswith('/'):
        link = link + '.html'
    
    return link

def create_nav(current='index'):
    """Create navigation HTML"""
    nav = '''    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="memos/index.html">Memos</a></li>
            <li><a href="sops/index.html">SOPs</a></li>
        </ul>
    </nav>'''
    return nav

def create_memo_nav():
    """Create navigation for memo pages"""
    nav = '''    <nav>
        <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="index.html">Memos</a></li>
            <li><a href="../sops/index.html">SOPs</a></li>
        </ul>
    </nav>'''
    return nav

def create_index_nav():
    """Create navigation for index page"""
    nav = '''    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="memos/index.html">Memos</a></li>
            <li><a href="sops/index.html">SOPs</a></li>
        </ul>
    </nav>'''
    return nav

def create_sop_nav():
    """Create navigation for SOP pages"""
    nav = '''    <nav>
        <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="../memos/index.html">Memos</a></li>
            <li><a href="index.html">SOPs</a></li>
        </ul>
    </nav>'''
    return nav

def create_html_template(title, content, nav_html, is_memo=False, memo_filename=None, is_sop=False):
    """Create complete HTML page"""
    css_path = '../assets/css/styles.css' if (is_memo or is_sop) else 'assets/css/styles.css'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CMDP Compliance</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
    <header>
        <h1>CMDP Compliance Documents</h1>
    </header>
{nav_html}
    <main>
{content}'''
    
    if is_memo and memo_filename:
        pdf_filename = memo_filename.replace('.docx', '.pdf')
        pdf_path = '../assets/pdf/' + pdf_filename
        word_path = '../assets/word/memos/' + memo_filename
        
        html += f'''
        <div class="document-viewer">
            <iframe src="{pdf_path}" type="application/pdf" width="100%" height="800px">
                <p>Your browser does not support PDFs. <a href="{pdf_path}">Download the PDF</a>.</p>
            </iframe>
        </div>
        <div class="download-section">
            <a href="{word_path}" class="download-btn" download>Download Word Template</a>
        </div>
'''
    
    html += '''    </main>
    <footer>
        <p>CMDP Compliance Documentation - FY24-25</p>
    </footer>
</body>
</html>'''
    
    return html

# Main conversion functions
def convert_index():
    """Convert main index page from source/cmdp-index.md only.

    The curated repo root index.html is preserved when cmdp-index.md is absent
    (see source/index.md for a folder readme, not the public home page).
    """
    md_file = _ROOT / "source" / "cmdp-index.md"
    if not md_file.exists():
        print(
            "Skipping index.html: source/cmdp-index.md not found "
            "(keeping existing curated index.html)."
        )
        return
    
    content = md_file.read_text(encoding='utf-8')
    html_content = markdown_to_html_simple(content)
    
    # Add intro section
    intro = '''        <div class="intro">
            <h2>About CMDP</h2>
            <p>The Command Maintenance Discipline Program (CMDP) establishes the minimum inspection requirements that all units must meet in order to maintain Army-standard maintenance discipline.</p>
            <p>This site provides access to all required memorandums and SOPs needed to achieve <strong>GO ratings</strong> during FY24-25 CMDP inspections.</p>
            <p><strong>What you'll find on this site:</strong></p>
            <ul>
                <li><strong>Memorandums:</strong> Appointment letters and program memorandums required for CMDP compliance</li>
                <li><strong>SOPs:</strong> Standard Operating Procedures covering maintenance, driver training, environmental, and other critical areas</li>
                <li><strong>Downloads:</strong> Word document templates for all memorandums and SOPs</li>
            </ul>
        </div>
'''
    
    full_content = intro + html_content
    
    html = create_html_template('CMDP Compliance Index', full_content, create_index_nav())
    
    Path(_ROOT / "index.html").write_text(html, encoding='utf-8')
    print("Created index.html")

def convert_memos_index():
    """Convert memos index"""
    md_file = _ROOT / "source" / "memos" / "memos.index.md"
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    html_content = markdown_to_html_simple(content)
    
    # Normalize any markdown-authored stylesheet hrefs for memo pages
    html_content = html_content.replace('css/styles.css', '../assets/css/styles.css')
    
    html = create_html_template('Memos Index', html_content, create_memo_nav())
    
    # Fix CSS path in the template too
    html = html.replace('css/styles.css', '../assets/css/styles.css')
    
    Path(_ROOT / "memos" / "index.html").write_text(html, encoding='utf-8')
    print("Created memos/index.html")

def convert_memo_page(md_file_path):
    """Convert individual memo page"""
    md_file = Path(md_file_path)
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    
    # Extract title from first heading or filename
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = md_file.stem.replace('-', ' ').title()
    
    # Clean content - remove navigation links and images
    lines = content.split('\n')
    cleaned_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        
        # Skip Obsidian navigation links
        if line.strip().startswith('[[') and ('memos.index' in line or 'cmdp-index' in line or '|' in line):
            continue
        # Skip image references
        if line.strip().startswith('!['):
            continue
        # Skip horizontal rules before signature
        if line.strip() == '---' and i + 1 < len(lines) and 'Respectfully' in lines[i + 1]:
            continue
        
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    html_content = markdown_to_html_simple(cleaned_content)
    
    # Get corresponding Word doc filename
    word_filename = md_file.stem + '.docx'
    if not (_ROOT / "assets" / "word" / "memos" / word_filename).exists():
        word_filename = None
    
    html = create_html_template(title, html_content, create_memo_nav(), 
                                is_memo=True, memo_filename=word_filename)
    
    # Create HTML filename
    html_filename = md_file.stem + '.html'
    Path(_ROOT / "memos" / html_filename).write_text(html, encoding='utf-8')
    print(f"Created memos/{html_filename}")

def convert_sops_index():
    """Convert SOPs index"""
    md_file = _ROOT / "source" / "sops" / "sops.index.md"
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    html_content = markdown_to_html_simple(content)
    
    html = create_html_template('SOPs Index', html_content, create_sop_nav())
    
    Path(_ROOT / "sops" / "index.html").write_text(html, encoding='utf-8')
    print("Created sops/index.html")

def convert_sop_page(md_file_path):
    """Convert individual SOP page"""
    md_file = Path(md_file_path)
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    
    # Extract title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = md_file.stem.replace('-', ' ').replace('sop', 'SOP').title()
    
    # Clean content
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip Obsidian navigation links
        if line.strip().startswith('[[') and ('sops.index' in line or 'cmdp-index' in line or '|' in line):
            continue
        
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    html_content = markdown_to_html_simple(cleaned_content)
    
    # Check for Word doc (SOP templates live under assets/word/sops)
    word_filename = md_file.stem + '.docx'
    if (_ROOT / "assets" / "word" / "sops" / word_filename).exists():
        download_section = f'''
        <div class="download-section">
            <a href="../assets/word/sops/{word_filename}" class="download-btn" download>Download Word Template</a>
        </div>'''
        html_content += download_section
    
    html = create_html_template(title, html_content, create_sop_nav(), is_sop=True)
    
    html_filename = md_file.stem + '.html'
    Path(_ROOT / "sops" / html_filename).write_text(html, encoding='utf-8')
    print(f"Created sops/{html_filename}")

if __name__ == '__main__':
    print("Building HTML site...")
    (_ROOT / "memos").mkdir(parents=True, exist_ok=True)
    (_ROOT / "sops").mkdir(parents=True, exist_ok=True)

    # Convert main index
    convert_index()
    
    # Convert memos index
    convert_memos_index()
    
    # Convert all memo pages
    memo_files = list((_ROOT / "source" / "memos").glob('*.md'))
    memo_files = [f for f in memo_files if f.name not in ['memos.index.md', '00.0-example-memo.md']]
    for memo_file in sorted(memo_files):
        convert_memo_page(memo_file)
    
    # Convert SOPs index
    convert_sops_index()
    
    # Convert all SOP pages
    sop_files = list((_ROOT / "source" / "sops").glob('*.md'))
    sop_files = [
        f
        for f in sop_files
        if f.name not in ('sops.index.md', 'SOP-template.md', '00.0.0.0-SOP-template.md')
        and f.name not in SOP_PIPELINE_MD_SKIP
        and not f.name.endswith('-dispatch-old.md')
    ]
    for sop_file in sorted(sop_files):
        convert_sop_page(sop_file)
    
    print("\nHTML site build complete!")

