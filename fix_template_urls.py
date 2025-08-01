#!/usr/bin/env python3
"""
Fix template URLs - Replace main.index with items.index
Run: python fix_template_urls.py
"""
import os
import re

def fix_template_files():
    """Fix all template files that use main.index"""
    
    # Define paths to check
    template_dirs = [
        'app/templates',
        'app/templates/layout',
        'app/templates/errors',
        'app/templates/items',
        'app/templates/admin',
        'app/templates/auth'
    ]
    
    files_fixed = 0
    files_checked = 0
    
    print("🔍 Searching for templates with 'main.index'...")
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue
            
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(template_dir, filename)
                files_checked += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file contains main.index
                    if 'main.index' in content:
                        # Replace main.index with items.index
                        new_content = content.replace("url_for('main.index')", "url_for('items.index')")
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"✅ Fixed: {filepath}")
                        files_fixed += 1
                        
                except Exception as e:
                    print(f"❌ Error processing {filepath}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Files checked: {files_checked}")
    print(f"   Files fixed: {files_fixed}")
    
    # Also check base.html specifically
    base_paths = [
        'app/templates/base.html',
        'app/templates/layout/base.html'
    ]
    
    print("\n🔍 Checking base.html files...")
    for base_path in base_paths:
        if os.path.exists(base_path):
            print(f"✅ Found: {base_path}")
            
            # Create a backup
            backup_path = base_path + '.backup_mainindex'
            try:
                with open(base_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Backup original
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📋 Backup created: {backup_path}")
                
            except Exception as e:
                print(f"⚠️  Could not backup {base_path}: {e}")

if __name__ == '__main__':
    fix_template_files()
    print("\n✨ Done! Please restart your Flask application.")
