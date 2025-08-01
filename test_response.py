#!/usr/bin/env python3
"""
Test what's happening with the response
Run: python test_response.py
"""
from app import create_app
from flask import url_for

app = create_app()

with app.app_context():
    print("🧪 Testing Response Issues\n")
    
    # Test 1: Check if detail route exists
    print("1. Testing detail route:")
    try:
        with app.test_request_context():
            detail_url = url_for('items.detail', id=1)
            print(f"   ✅ Detail URL: {detail_url}")
    except Exception as e:
        print(f"   ❌ Error generating detail URL: {e}")
    
    # Test 2: Check templates
    print("\n2. Checking templates:")
    import os
    templates = [
        'app/templates/items/detail.html',
        'app/templates/items/add.html',
        'app/templates/items/index.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - MISSING!")
    
    # Test 3: Check if redirect is imported
    print("\n3. Checking imports in routes.py:")
    routes_file = 'app/items/routes.py'
    if os.path.exists(routes_file):
        with open(routes_file, 'r') as f:
            content = f.read()
            
        if 'from flask import' in content and 'redirect' in content:
            print("   ✅ redirect is imported")
        else:
            print("   ❌ redirect is NOT imported!")
            
        if 'make_response' in content:
            print("   ⚠️  make_response is used (might cause issues)")
        
        if 'HX-Redirect' in content:
            print("   ⚠️  HX-Redirect headers found (might cause issues)")
    
    print("\n📋 Diagnosis:")
    print("If you see HTML code after saving, it's likely because:")
    print("1. The detail route doesn't exist")
    print("2. The detail template is missing")
    print("3. The response is returning HTML instead of redirecting")
    print("4. make_response() is being used incorrectly")
