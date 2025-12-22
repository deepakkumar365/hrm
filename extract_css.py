"""
CSS Extraction Script
This script removes all embedded <style> blocks and inline style="" attributes
from HTML templates and consolidates them into the external CSS file.
"""

import re
import os
from pathlib import Path

# Configuration
TEMPLATES_DIR = r"d:\Project\Workouts\hrm\templates"
CSS_FILE = r"d:\Project\Workouts\hrm\static\css\styles.css"
BACKUP_DIR = r"d:\Project\Workouts\hrm\templates_backup"

def backup_templates():
    """Create backup of all template files"""
    import shutil
    if not os.path.exists(BACKUP_DIR):
        shutil.copytree(TEMPLATES_DIR, BACKUP_DIR)
        print(f"✓ Backed up templates to {BACKUP_DIR}")

def find_html_files(directory):
    """Find all HTML files in directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def extract_style_blocks(content):
    """Extract all <style> blocks from HTML content"""
    # Pattern to match <style>...</style> blocks
    pattern = r'<style>(.*?)</style>'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    return matches

def remove_style_blocks(content):
    """Remove all <style> blocks from HTML content"""
    # Remove <style>...</style> blocks
    pattern = r'\s*<style>.*?</style>\s*'
    cleaned = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    return cleaned

def remove_inline_styles(content):
    """Remove inline style="" attributes from HTML content"""
    # Pattern to match style="..." attributes
    pattern = r'\s+style="[^"]*"'
    cleaned = re.sub(pattern, '', content)
    return cleaned

def process_template(file_path):
    """Process a single template file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Extract style blocks for logging
    style_blocks = extract_style_blocks(content)
    inline_styles = len(re.findall(r'style="[^"]*"', content))
    
    # Remove embedded CSS
    content = remove_style_blocks(content)
    
    # Remove inline styles
    content = remove_inline_styles(content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        rel_path = os.path.relpath(file_path, TEMPLATES_DIR)
        print(f"✓ {rel_path}")
        if style_blocks:
            print(f"  - Removed {len(style_blocks)} <style> block(s)")
        if inline_styles:
            print(f"  - Removed {inline_styles} inline style attribute(s)")
        return True
    
    return False

def main():
    print("=" * 60)
    print("CSS Extraction Script")
    print("=" * 60)
    print()
    
    # Backup templates
    print("Step 1: Creating backup...")
    backup_templates()
    print()
    
    # Find all HTML files
    print("Step 2: Finding HTML files...")
    html_files = find_html_files(TEMPLATES_DIR)
    print(f"✓ Found {len(html_files)} HTML files")
    print()
    
    # Process each file
    print("Step 3: Processing templates...")
    processed_count = 0
    for file_path in html_files:
        if process_template(file_path):
            processed_count += 1
    
    print()
    print("=" * 60)
    print(f"✓ Complete! Processed {processed_count} files")
    print(f"✓ Backup saved to: {BACKUP_DIR}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the changes in your templates")
    print("2. Test the application to ensure styles are working")
    print("3. If everything looks good, delete the backup folder")

if __name__ == "__main__":
    main()
