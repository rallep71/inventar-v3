#!/usr/bin/env python3
"""
Fix all route issues in the application
Run: python fix_all_routes.py
"""
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of a file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def fix_admin_init():
    """Fix app/admin/__init__.py"""
    admin_init_path = 'app/admin/__init__.py'
    
    content = '''# app/admin/__init__.py
"""Admin panel blueprint"""
from flask import Blueprint

admin = Blueprint('admin', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.admin import routes
'''
    
    try:
        if os.path.exists(admin_init_path):
            backup_file(admin_init_path)
        
        os.makedirs(os.path.dirname(admin_init_path), exist_ok=True)
        with open(admin_init_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {admin_init_path}")
    except Exception as e:
        print(f"❌ Error fixing {admin_init_path}: {e}")

def fix_admin_routes():
    """Ensure admin routes exist"""
    admin_routes_path = 'app/admin/routes.py'
    
    if not os.path.exists(admin_routes_path):
        content = '''# app/admin/routes.py
"""Admin panel routes"""
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.admin import admin

@admin.route('/')
@login_required
def index():
    """Admin dashboard"""
    # Temporarily return a simple page
    return "<h1>Admin Dashboard - Coming Soon</h1><p><a href='/items'>Back to Items</a></p>"
'''
        
        try:
            with open(admin_routes_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created: {admin_routes_path}")
        except Exception as e:
            print(f"❌ Error creating {admin_routes_path}: {e}")

def fix_main_routes():
    """Fix app/main/routes.py"""
    main_routes_path = 'app/main/routes.py'
    
    content = '''# app/main/routes.py
"""Main blueprint routes"""
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main


@main.route('/')
def index():
    """Homepage - redirect to items if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('items.index'))
    return redirect(url_for('auth.login'))


@main.route('/home')
def home():
    """Alternative home route"""
    return index()
'''
    
    try:
        if os.path.exists(main_routes_path):
            backup_file(main_routes_path)
        
        os.makedirs(os.path.dirname(main_routes_path), exist_ok=True)
        with open(main_routes_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {main_routes_path}")
    except Exception as e:
        print(f"❌ Error fixing {main_routes_path}: {e}")

def fix_template_urls():
    """Fix all template URL issues"""
    replacements = {
        "url_for('main.index')": "url_for('items.index')",
        "url_for('main.home')": "url_for('items.index')",
    }
    
    template_dirs = [
        'app/templates',
        'app/templates/layout',
        'app/templates/errors',
        'app/templates/items',
        'app/templates/admin',
        'app/templates/auth'
    ]
    
    files_fixed = 0
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue
            
        for root, dirs, files in os.walk(template_dir):
            for filename in files:
                if filename.endswith('.html'):
                    filepath = os.path.join(root, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply all replacements
                        for old, new in replacements.items():
                            content = content.replace(old, new)
                        
                        # Only write if changed
                        if content != original_content:
                            backup_file(filepath)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"✅ Fixed: {filepath}")
                            files_fixed += 1
                            
                    except Exception as e:
                        print(f"❌ Error processing {filepath}: {e}")
    
    return files_fixed

def ensure_auth_logout():
    """Ensure auth logout is POST only"""
    auth_routes_path = 'app/auth/routes.py'
    
    # Check if logout route needs fixing
    if os.path.exists(auth_routes_path):
        try:
            with open(auth_routes_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if logout accepts GET
            if "@auth.route('/logout')" in content and "methods=['POST']" not in content:
                print("⚠️  Warning: auth.logout should only accept POST requests")
                print("   Consider updating the logout links to use forms with POST method")
        except Exception as e:
            print(f"❌ Error checking {auth_routes_path}: {e}")

def main():
    print("🔧 Fixing route and template issues...\n")
    
    # Fix route files
    fix_admin_init()
    fix_admin_routes()
    fix_main_routes()
    
    # Fix templates
    print("\n📝 Fixing template URLs...")
    fixed_count = fix_template_urls()
    print(f"   Fixed {fixed_count} template files")
    
    # Check auth logout
    ensure_auth_logout()
    
    print("\n✨ Done! Please restart your Flask application:")
    print("   1. Stop the server (Ctrl+C)")
    print("   2. Clear cache: find . -name '*.pyc' -delete")
    print("   3. Start again: python run.py")

if __name__ == '__main__':
    main()
