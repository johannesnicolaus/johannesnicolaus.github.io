#!/usr/bin/env python3
"""Convert HTML blog posts to Markdown format."""

import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from io import StringIO

# Simple HTML to Markdown converter
class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        if tag in ['p', 'div']:
            if self.text and self.text[-1] != '\n\n':
                self.text.append('\n\n')
        elif tag == 'br':
            self.text.append('\n')
        elif tag == 'b' or tag == 'strong':
            self.text.append('**')
            self.tag_stack.append(tag)
        elif tag == 'i' or tag == 'em':
            self.text.append('*')
            self.tag_stack.append(tag)
        elif tag == 'a':
            self.text.append('[')
            self.tag_stack.append(('a', dict(attrs)))
            
    def handle_endtag(self, tag):
        if tag in ['p', 'div']:
            if self.text and self.text[-1] != '\n\n':
                self.text.append('\n\n')
        elif tag == 'b' or tag == 'strong':
            if self.tag_stack and self.tag_stack[-1] in ['b', 'strong']:
                self.text.append('**')
                self.tag_stack.pop()
        elif tag == 'i' or tag == 'em':
            if self.tag_stack and self.tag_stack[-1] in ['i', 'em']:
                self.text.append('*')
                self.tag_stack.pop()
        elif tag == 'a':
            if self.tag_stack and isinstance(self.tag_stack[-1], tuple):
                tag_info = self.tag_stack.pop()
                href = dict(tag_info[1]).get('href', '#')
                self.text.append(f']({href})')
                
    def handle_data(self, data):
        # Clean up excessive whitespace
        data = data.replace('\r', '')
        lines = data.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        if cleaned_lines:
            self.text.append(' '.join(cleaned_lines))
    
    def get_markdown(self):
        result = ''.join(self.text).strip()
        # Clean up multiple newlines
        result = re.sub(r'\n\n+', '\n\n', result)
        # Clean up orphaned formatting
        result = re.sub(r'\*\*\s*\*\*', '', result)
        result = re.sub(r'\*\s*\*', '', result)
        return result


def extract_yaml_frontmatter(html_content):
    """Extract YAML front matter from HTML file."""
    match = re.match(r'^---\n(.*?)\n---\n', html_content, re.DOTALL)
    if match:
        return match.group(1), html_content[match.end():]
    return None, html_content


def convert_html_to_markdown(html_file_path):
    """Convert HTML blog post to Markdown format."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    frontmatter, body = extract_yaml_frontmatter(content)
    
    if not frontmatter:
        print(f"⚠️  No YAML frontmatter found in {html_file_path}")
        return False
    
    # Parse HTML body to Markdown
    converter = HTMLToMarkdownConverter()
    converter.feed(body)
    markdown_body = converter.get_markdown()
    
    # Extract excerpt (first paragraph)
    excerpt_match = re.match(r'^([^\n]+)', markdown_body)
    excerpt = excerpt_match.group(1) if excerpt_match else "See full post..."
    excerpt = excerpt[:200] + '...' if len(excerpt) > 200 else excerpt
    
    # Update frontmatter
    frontmatter_lines = frontmatter.strip().split('\n')
    # Remove layout if it's "posts", change to "single"
    frontmatter_lines = [line for line in frontmatter_lines if not line.startswith('layout:')]
    frontmatter_lines.append('layout: single')
    
    # Remove blogger-specific fields
    frontmatter_lines = [line for line in frontmatter_lines if not any(x in line.lower() for x in ['blogger', 'thumbnail'])]
    
    # Add excerpt if not present
    if not any('excerpt:' in line for line in frontmatter_lines):
        frontmatter_lines.append(f'excerpt: "{excerpt}"')
    
    new_frontmatter = '\n'.join(frontmatter_lines)
    
    # Create new markdown content
    new_content = f"---\n{new_frontmatter}\n---\n\n{markdown_body}\n"
    
    # Create output filename
    base_name = Path(html_file_path).stem
    md_file_path = html_file_path.replace('.html', '.md')
    
    # Write new markdown file
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Converted: {base_name}.html → {Path(md_file_path).name}")
    return True


def main():
    posts_dir = Path('_posts')
    
    if not posts_dir.exists():
        print("Error: _posts directory not found")
        sys.exit(1)
    
    html_files = list(posts_dir.glob('*.html'))
    
    if not html_files:
        print("No HTML files found in _posts directory")
        return
    
    print(f"Found {len(html_files)} HTML blog posts to convert\n")
    
    converted = 0
    for html_file in sorted(html_files):
        if convert_html_to_markdown(str(html_file)):
            converted += 1
    
    print(f"\n✓ Successfully converted {converted}/{len(html_files)} files")
    print("Note: Original HTML files remain. Delete them manually if desired.")


if __name__ == '__main__':
    main()
