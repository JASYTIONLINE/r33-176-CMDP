import re
from pathlib import Path

def clean_obsidian_link(link_text):
    """Extract filename from Obsidian link"""
    # Handle [[link|text]] or [[link]]
    match = re.match(r'\[\[([^\]]+)(?:\|([^\]]+))?\]\]', link_text)
    if match:
        link = match.group(1)
        # Remove .md extension and path prefixes
        link = link.replace('.md', '')
        link = link.replace('memos/', '')
        link = link.replace('content/sops/', '')
        link = link.replace('content/memos/', '')
        # Convert to HTML filename
        if 'sop-' in link:
            link = link.replace('sop-', 'sop-').replace('_', '-')
        link = link.replace('_', '-')
        return link
    return None

def markdown_to_html_simple(md_text):
    """Convert basic markdown to HTML"""
    html = md_text
    
    # Remove image syntax
    html = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', html)
    
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
                
                # Wrap in paragraph if not already a header or list
                if not re.match(r'^<[hH]', stripped) and not stripped.startswith('<ul') and not stripped.startswith('<ol'):
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
    if link.startswith('content/sops/'):
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
    css_path = '../css/styles.css' if (is_memo or is_sop) else 'css/styles.css'
    
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
        word_path = '../content/word/' + memo_filename
        
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
    """Convert main index page"""
    md_file = Path('content/cmdp-index.md')
    if not md_file.exists():
        print(f"Error: {md_file} not found")
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
    
    Path('index.html').write_text(html, encoding='utf-8')
    print("Created index.html")

def convert_memos_index():
    """Convert memos index"""
    md_file = Path('content/memos/memos.index.md')
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    html_content = markdown_to_html_simple(content)
    
    # Fix CSS path (should be ../css/styles.css from memos folder)
    html_content = html_content.replace('css/styles.css', '../css/styles.css')
    
    html = create_html_template('Memos Index', html_content, create_memo_nav())
    
    # Fix CSS path in the template too
    html = html.replace('css/styles.css', '../css/styles.css')
    
    Path('memos/index.html').write_text(html, encoding='utf-8')
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
    if not Path(f'content/word/{word_filename}').exists():
        word_filename = None
    
    html = create_html_template(title, html_content, create_memo_nav(), 
                                is_memo=True, memo_filename=word_filename)
    
    # Create HTML filename
    html_filename = md_file.stem + '.html'
    Path(f'memos/{html_filename}').write_text(html, encoding='utf-8')
    print(f"Created memos/{html_filename}")

def convert_sops_index():
    """Convert SOPs index"""
    md_file = Path('content/sops/sops.index.md')
    if not md_file.exists():
        print(f"Error: {md_file} not found")
        return
    
    content = md_file.read_text(encoding='utf-8')
    html_content = markdown_to_html_simple(content)
    
    html = create_html_template('SOPs Index', html_content, create_sop_nav())
    
    Path('sops/index.html').write_text(html, encoding='utf-8')
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
        # Skip image references
        if line.strip().startswith('!['):
            continue
        
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    html_content = markdown_to_html_simple(cleaned_content)
    
    # Check for Word doc
    word_filename = md_file.stem + '.docx'
    if Path(f'content/word/{word_filename}').exists():
        download_section = f'''
        <div class="download-section">
            <a href="../content/word/{word_filename}" class="download-btn" download>Download Word Template</a>
        </div>'''
        html_content += download_section
    
    html = create_html_template(title, html_content, create_sop_nav(), is_sop=True)
    
    html_filename = md_file.stem + '.html'
    Path(f'sops/{html_filename}').write_text(html, encoding='utf-8')
    print(f"Created sops/{html_filename}")

if __name__ == '__main__':
    print("Building HTML site...")
    
    # Convert main index
    convert_index()
    
    # Convert memos index
    convert_memos_index()
    
    # Convert all memo pages
    memo_files = list(Path('content/memos').glob('*.md'))
    memo_files = [f for f in memo_files if f.name not in ['memos.index.md', '00.0-example-memo.md']]
    for memo_file in sorted(memo_files):
        convert_memo_page(memo_file)
    
    # Convert SOPs index
    convert_sops_index()
    
    # Convert all SOP pages
    sop_files = list(Path('content/sops').glob('*.md'))
    sop_files = [f for f in sop_files if f.name != 'sops.index.md']
    for sop_file in sorted(sop_files):
        convert_sop_page(sop_file)
    
    print("\nHTML site build complete!")

