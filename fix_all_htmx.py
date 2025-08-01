#!/usr/bin/env python3
"""
Entfernt ALLE HX-Redirect aus ALLEN Funktionen
Run: python fix_all_htmx.py
"""
import re

# Backup
import shutil
shutil.copy('app/items/routes.py', 'app/items/routes.py.backup_all_htmx')

with open('app/items/routes.py', 'r') as f:
    content = f.read()

# Entferne ALLE HX-Redirect Patterns
patterns_to_remove = [
    # Pattern 1: if HX-Request mit response manipulation
    (r'if request\.headers\.get\([\'"]HX-Request[\'"]\):.*?return response', 
     'return render_template'),
    
    # Pattern 2: make_response mit HX-Redirect
    (r'response = make_response\(\).*?response\.headers\[[\'"]HX-Redirect[\'"]\].*?return response',
     'return render_template'),
     
    # Pattern 3: Nur HX-Redirect header setzen
    (r'response\.headers\[[\'"]HX-Redirect[\'"]\] = .*?\n', ''),
    
    # Pattern 4: HTMX spezifische returns
    (r'if request\.headers\.get\([\'"]HX-Request[\'"]\):.*?return.*?\n.*?return', 
     'return'),
]

for pattern, replacement in patterns_to_remove:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Spezialfix für items_grid partial returns
content = re.sub(
    r'return render_template\([\'"]items/partials/items_grid\.html[\'"]',
    'return render_template(\'items/index.html\'',
    content
)

with open('app/items/routes.py', 'w') as f:
    f.write(content)

print("✅ Alle HX-Redirect entfernt!")
print("🚀 Starte Flask neu: python run.py")
