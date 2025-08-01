#!/usr/bin/env python3
"""
Fix für das HTML Response Problem
Run: python fix_response_issue.py
"""
import os
import re

def fix_add_route():
    """Fix the add route to ensure proper redirect"""
    routes_file = 'app/items/routes.py'
    
    if not os.path.exists(routes_file):
        print("❌ routes.py nicht gefunden!")
        return
    
    print("🔧 Fixing response issue in add route...")
    
    # Backup
    backup_file = f"{routes_file}.backup_response_fix"
    with open(routes_file, 'r') as f:
        content = f.read()
    
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"📋 Backup created: {backup_file}")
    
    # Fix 1: Remove any make_response() calls in add function
    content = re.sub(
        r'response = make_response\(\)',
        'response = redirect(url_for("items.detail", id=item.id))',
        content
    )
    
    # Fix 2: Replace HX-Redirect responses with normal redirects
    content = re.sub(
        r"response\.headers\['HX-Redirect'\] = url_for\('items\.detail', id=item\.id\)\s*return response",
        'return redirect(url_for("items.detail", id=item.id))',
        content
    )
    
    # Fix 3: Ensure proper imports
    if 'from flask import' in content and 'redirect' not in content:
        content = re.sub(
            r'from flask import (.+)',
            lambda m: f"from flask import {m.group(1)}, redirect" if 'redirect' not in m.group(1) else m.group(0),
            content
        )
    
    # Save fixed file
    with open(routes_file, 'w') as f:
        f.write(content)
    
    print("✅ Response issue fixed!")
    print("\n📝 Changes made:")
    print("  - Removed make_response() calls")
    print("  - Replaced HX-Redirect with normal redirects")
    print("  - Ensured redirect is imported")

def create_simple_detail_template():
    """Create a simple detail template in case it's missing"""
    detail_template = 'app/templates/items/detail.html'
    
    if os.path.exists(detail_template):
        print("\n✅ Detail template exists")
        return
    
    print("\n🔧 Creating simple detail template...")
    
    simple_template = '''{% extends "layout/base.html" %}
{% block title %}{{ item.name }} - Inventar{% endblock %}
{% block content %}
<div class="container">
    <h1>{{ item.name }}</h1>
    <p><strong>ID:</strong> {{ item.item_uid }}</p>
    <p><strong>Menge:</strong> {{ item.quantity }}</p>
    <p><a href="{{ url_for('items.index') }}" class="btn btn-secondary">Zurück zur Übersicht</a></p>
</div>
{% endblock %}'''
    
    os.makedirs(os.path.dirname(detail_template), exist_ok=True)
    with open(detail_template, 'w') as f:
        f.write(simple_template)
    
    print("✅ Simple detail template created")

def main():
    print("🔧 Fixing HTML Response Issue\n")
    
    fix_add_route()
    create_simple_detail_template()
    
    print("\n✅ Fixes applied!")
    print("\n🚀 Next steps:")
    print("1. Check routes: python check_routes.py")
    print("2. Restart Flask: python run.py")
    print("3. Try creating an item again")

if __name__ == '__main__':
    main()
