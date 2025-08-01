#!/usr/bin/env python3
"""
Sicherer Fix NUR für die detail() Funktion
Run: python safe_detail_fix.py
"""
import re

print("🔧 Fixing detail() function only...\n")

with open('app/items/routes.py', 'r') as f:
    content = f.read()

# Backup
with open('app/items/routes.py.backup_detail_fix', 'w') as f:
    f.write(content)

# Finde nur die detail() Funktion
detail_match = re.search(r'(@items\.route\("/(?:<int:id>|<item_uid>)".*?\)\s*@login_required\s*def detail\(.*?\):.*?)(?=@items\.route|def\s+\w+|$)', content, re.DOTALL)

if detail_match:
    detail_func = detail_match.group(0)
    print("✅ Found detail() function")
    
    # Fix nur diese Funktion
    fixed_detail = detail_func
    
    # Entferne HX-Redirect Zeilen
    fixed_detail = re.sub(r'\s*response\.headers\[[\'"]HX-Redirect[\'"].*?\n', '', fixed_detail)
    
    # Entferne if HX-Request blocks
    fixed_detail = re.sub(
        r'\s*if request\.headers\.get\([\'"]HX-Request[\'"]\):.*?return.*?\n\s*return',
        '\n    return',
        fixed_detail,
        flags=re.DOTALL
    )
    
    # Ersetze im content
    content = content.replace(detail_func, fixed_detail)
    
    # Speichern
    with open('app/items/routes.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed detail() function!")
else:
    print("❌ Could not find detail() function")

print("\nTest syntax...")
try:
    compile(open('app/items/routes.py').read(), 'routes.py', 'exec')
    print("✅ Syntax OK!")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    print("Restoring backup...")
    import shutil
    shutil.copy('app/items/routes.py.backup_detail_fix', 'app/items/routes.py')
    print("✅ Restored")
