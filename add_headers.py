#!/usr/bin/env python3
"""
Add standardized headers to all knowledge base markdown files
"""

import os
import re
from datetime import datetime
from pathlib import Path

def extract_metadata_from_filename(filename):
    """Extract date and title from filename pattern: YYYYMMDD_HHMMSS_Title.md"""
    pattern = r'(\d{8})_(\d{6})_(.+)\.md$'
    match = re.match(pattern, filename)
    
    if match:
        date_str, time_str, title = match.groups()
        # Parse date and time
        date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        time = datetime.strptime(time_str, '%H%M%S').strftime('%H:%M:%S')
        # Clean up title (replace underscores with spaces)
        title = title.replace('_', ' ')
        return date, time, title
    return None, None, None

def extract_metadata_from_content(content):
    """Try to extract metadata from existing content"""
    lines = content.split('\n')
    
    # Check if header already exists
    if lines and lines[0].startswith('---'):
        # Header might already exist
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break
        if end_index > 0:
            return True, None  # Header exists
    
    # Try to find title from first heading
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    return False, title

def create_header(date, time, title, doc_type, tags=None, status='active'):
    """Create a standardized header"""
    if tags is None:
        tags = []
    
    header = f"""---
title: "{title}"
date: {date}
time: {time}
type: {doc_type}
status: {status}
tags: [{', '.join(f'"{tag}"' for tag in tags)}]
---

"""
    return header

def infer_doc_type(filepath):
    """Infer document type from filepath"""
    path_parts = Path(filepath).parts
    
    if 'research' in path_parts:
        return 'research'
    elif 'midnight' in path_parts or 'documentation' in str(filepath).lower():
        return 'documentation'
    elif 'tutorial' in str(filepath).lower():
        return 'tutorial'
    elif 'reference' in str(filepath).lower():
        return 'reference'
    else:
        return 'general'

def infer_tags(filepath, title, content):
    """Infer tags from filepath, title, and content"""
    tags = set()
    
    # From filepath
    path_str = str(filepath).lower()
    if 'midnight' in path_str:
        tags.add('midnight')
    if 'zero-knowledge' in path_str or 'zk' in path_str:
        tags.add('zero-knowledge')
    if 'privacy' in path_str:
        tags.add('privacy')
    if 'blockchain' in path_str:
        tags.add('blockchain')
    
    # From title
    title_lower = title.lower()
    if 'proof' in title_lower or 'zk' in title_lower:
        tags.add('cryptography')
    if 'smart contract' in title_lower:
        tags.add('smart-contracts')
    if 'tutorial' in title_lower or 'guide' in title_lower:
        tags.add('tutorial')
    
    # From content (first 500 chars)
    content_sample = content[:500].lower()
    keywords = {
        'privacy': 'privacy',
        'transaction': 'transactions',
        'proof': 'cryptography',
        'contract': 'smart-contracts',
        'validator': 'consensus',
        'token': 'tokens',
        'dapp': 'dapps'
    }
    
    for keyword, tag in keywords.items():
        if keyword in content_sample:
            tags.add(tag)
    
    return sorted(list(tags))

def add_header_to_file(filepath, dry_run=False, backup=True):
    """Add header to a single file"""
    try:
        # Read existing content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if header already exists
        has_header, extracted_title = extract_metadata_from_content(content)
        
        if has_header:
            print(f"⏭️  Skipping (has header): {filepath}")
            return 'skipped'
        
        # Extract metadata from filename
        filename = os.path.basename(filepath)
        date, time, title_from_filename = extract_metadata_from_filename(filename)
        
        # Use extracted title or filename title
        title = title_from_filename or extracted_title or filename.replace('.md', '').replace('_', ' ')
        
        # If no date/time from filename, use file modification time
        if not date or not time:
            mtime = os.path.getmtime(filepath)
            dt = datetime.fromtimestamp(mtime)
            date = dt.strftime('%Y-%m-%d')
            time = dt.strftime('%H:%M:%S')
        
        # Infer document type and tags
        doc_type = infer_doc_type(filepath)
        tags = infer_tags(filepath, title, content)
        
        # Create header
        header = create_header(date, time, title, doc_type, tags)
        
        # Combine header with content
        new_content = header + content
        
        if dry_run:
            print(f"🔍 Would add header to: {filepath}")
            print(f"   Title: {title}")
            print(f"   Type: {doc_type}")
            print(f"   Tags: {tags}")
            return 'dry_run'
        
        # Backup original file
        if backup:
            backup_path = f"{filepath}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Write new content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added header to: {filepath}")
        return 'success'
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return 'error'

def process_directory(directory, dry_run=False, backup=True, recursive=True):
    """Process all markdown files in a directory"""
    stats = {
        'success': 0,
        'skipped': 0,
        'error': 0,
        'dry_run': 0
    }
    
    kb_path = Path(directory)
    
    # Find all markdown files
    if recursive:
        md_files = list(kb_path.rglob('*.md'))
    else:
        md_files = list(kb_path.glob('*.md'))
    
    # Exclude INDEX.md
    md_files = [f for f in md_files if f.name != 'INDEX.md']
    
    print(f"\n{'='*60}")
    print(f"Found {len(md_files)} markdown files to process")
    print(f"Dry run: {dry_run}")
    print(f"Backup: {backup}")
    print(f"{'='*60}\n")
    
    for filepath in md_files:
        result = add_header_to_file(filepath, dry_run, backup)
        stats[result] += 1
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  ✅ Success: {stats['success']}")
    print(f"  ⏭️  Skipped: {stats['skipped']}")
    print(f"  ❌ Errors: {stats['error']}")
    if dry_run:
        print(f"  🔍 Would process: {stats['dry_run']}")
    print(f"{'='*60}\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Add standardized headers to knowledge base markdown files'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='./knowledge_base',
        help='Directory to process (default: ./knowledge_base)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not process subdirectories'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ Directory not found: {args.directory}")
        return
    
    process_directory(
        args.directory,
        dry_run=args.dry_run,
        backup=not args.no_backup,
        recursive=not args.no_recursive
    )

if __name__ == '__main__':
    main()