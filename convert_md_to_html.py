import re
from pathlib import Path

def clean_obsidian_links(text):
    """Convert Obsidian-style links to HTML links"""
    # Handle [[link|text]] format
    text = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', r'<a href="\1">\2</a>', text)
    # Handle [[link]] format
    text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="\1">\1</a>', text)
    return text

def markdown_to_html(md_text, base_path=''):
    """Convert markdown to HTML"""
    html = md_text
    
    # Remove Obsidian image syntax
    html = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'', html)
    
    # Convert headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold
    html = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic
    html = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', html)
    
    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    
    # Convert unordered lists
    lines = html.split('\n')
    in_list = False
    result = []
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            content = line.strip()[2:].strip()
            result.append(f'  <li>{content}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            if line.strip():
                result.append(f'<p>{line.strip()}</p>')
            else:
                result.append('')
    
    if in_list:
        result.append('</ul>')
    
    html = '\n'.join(result)
    
    # Clean up empty paragraphs
    html = re.sub(r'<p></p>', '', html)
    html = re.sub(r'<p>\s*</p>', '', html)
    
    # Convert Obsidian links
    html = clean_obsidian_links(html)
    
    return html

def create_navigation(current_page='index'):
    """Create navigation HTML"""
    nav_items = [
        ('index.html', 'Home'),
        ('memos/index.html', 'Memos'),
        ('sops/index.html', 'SOPs')
    ]
    
    nav_html = '<nav><ul>'
    for link, text in nav_items:
        if current_page == link.replace('.html', '').replace('/', '-'):
            nav_html += f'<li><a href="{link}" class="active">{text}</a></li>'
        else:
            nav_html += f'<li><a href="{link}">{text}</a></li>'
    nav_html += '</ul></nav>'
    
    return nav_html

def create_html_page(title, content, nav_html, is_memo=False, memo_filename=None, is_sop=False):
    """Create a complete HTML page"""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CMDP Compliance</title>
    <link rel="stylesheet" href="{'../' if is_memo or is_sop else ''}css/styles.css">
</head>
<body>
    <header>
        <h1>CMDP Compliance Documents</h1>
    </header>
    {nav_html}
    <main>
        {content}
'''
    
    if is_memo and memo_filename:
        # Add PDF viewer and download button
        pdf_path = f"{'../' if is_memo else ''}assets/pdf/{memo_filename.replace('.docx', '.pdf')}"
        word_path = f"{'../' if is_memo else ''}word/{memo_filename}"
        html += f'''
        <div class="document-viewer">
            <iframe src="{pdf_path}" type="application/pdf"></iframe>
        </div>
        <div class="download-section">
            <a href="{word_path}" class="download-btn" download>Download Word Template</a>
        </div>
'''
    
    html += '''
    </main>
    <footer>
        <p>CMDP Compliance Documentation - FY24-25</p>
    </footer>
</body>
</html>'''
    
    return html

if __name__ == '__main__':
    print("Markdown to HTML conversion utilities loaded.")

