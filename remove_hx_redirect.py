#!/usr/bin/env python3
"""
Entfernt alle HX-Redirect Headers aus routes.py
Run: python remove_hx_redirect.py
"""
import os
import re
from datetime import datetime

def remove_hx_redirect():
    routes_file = 'app/items/routes.py'
    
    if not os.path.exists(routes_file):
        print("❌ routes.py nicht gefunden!")
        return False
    
    # Backup erstellen
    backup_file = f"{routes_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(routes_file, 'r') as f:
        original_content = f.read()
    
    with open(backup_file, 'w') as f:
        f.write(original_content)
    print(f"📋 Backup erstellt: {backup_file}")
    
    # Content für Bearbeitung
    content = original_content
    
    # Pattern 1: HX-Request check mit Response-Erstellung
    pattern1 = r'''if\s+request\.headers\.get\(['"]HX-Request['"]\):\s*
\s*response\s*=\s*(?:make_response\(\)|redirect\([^)]+\))\s*
\s*response\.headers\[['"]HX-Redirect['"]\]\s*=\s*[^
]+\s*
\s*return\s+response'''
    
    # Ersetze mit einfachem redirect
    content = re.sub(pattern1, 
                    lambda m: "return redirect(url_for('items.detail', id=item.id))" if "detail" in m.group(0) else "return redirect(url_for('items.index'))",
                    content,
                    flags=re.MULTILINE | re.DOTALL)
    
    # Pattern 2: Nur HX-Redirect ohne if-check
    pattern2 = r'''response\s*=\s*make_response\(\)\s*
\s*response\.headers\[['"]HX-Redirect['"]\]\s*=\s*[^
]+\s*
\s*return\s+response'''
    
    content = re.sub(pattern2,
                    lambda m: "return redirect(url_for('items.detail', id=item.id))" if "detail" in m.group(0) else "return redirect(url_for('items.index'))",
                    content,
                    flags=re.MULTILINE | re.DOTALL)
    
    # Pattern 3: Vereinfachte Version
    content = re.sub(
        r"response\.headers\['HX-Redirect'\] = url_for\([^)]+\)",
        "",
        content
    )
    
    # Pattern 4: make_response import entfernen wenn nicht mehr gebraucht
    if 'make_response()' not in content and 'make_response' in content:
        content = re.sub(r',\s*make_response', '', content)
        content = re.sub(r'make_response,?\s*', '', content)
    
    # Speichern wenn Änderungen vorgenommen wurden
    if content != original_content:
        with open(routes_file, 'w') as f:
            f.write(content)
        print("✅ HX-Redirect Headers entfernt!")
        return True
    else:
        print("⚠️  Keine HX-Redirect Headers gefunden oder bereits entfernt")
        return False

def check_add_function():
    """Prüfe die add() Funktion speziell"""
    routes_file = 'app/items/routes.py'
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    # Finde die add Funktion
    add_func_match = re.search(r'def add\(.*?\):(.*?)(?=\ndef|\Z)', content, re.DOTALL)
    
    if add_func_match:
        add_content = add_func_match.group(1)
        
        print("\n🔍 Checking add() function:")
        
        if 'HX-Redirect' in add_content:
            print("   ❌ HX-Redirect noch vorhanden in add()")
            
            # Zeige die problematischen Zeilen
            lines = add_content.split('\n')
            for i, line in enumerate(lines):
                if 'HX-Redirect' in line or 'make_response' in line:
                    print(f"   Line {i}: {line.strip()}")
        else:
            print("   ✅ Keine HX-Redirect in add() gefunden")
        
        # Check für korrekten redirect
        if 'return redirect(url_for(' in add_content:
            print("   ✅ Normale redirect statements gefunden")
        else:
            print("   ⚠️  Keine redirect statements gefunden")

def main():
    print("🔧 Entferne HX-Redirect Headers\n")
    
    if remove_hx_redirect():
        print("\n✅ Erfolgreich gefixt!")
    
    check_add_function()
    
    print("\n🚀 Nächste Schritte:")
    print("1. Starte Flask neu: python run.py")
    print("2. Erstelle einen neuen Artikel")
    print("3. Du solltest jetzt korrekt weitergeleitet werden!")

if __name__ == '__main__':
    main()
