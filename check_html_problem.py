#!/bin/bash
# Zeigt genau wo das HTML-Problem ist

echo "🔍 SHOWING HTML RESPONSE PROBLEM"
echo "================================"

echo -e "\n📋 Detail function returns:"
echo "-------------------------"
awk '/def detail\(/,/^def|^@/' app/items/routes.py | grep -n "return" | grep -v "#"

echo -e "\n📋 Edit function returns:"
echo "-----------------------"
awk '/def edit\(/,/^def|^@/' app/items/routes.py | grep -n "return" | grep -v "#"

echo -e "\n⚠️  Looking for direct HTML returns:"
echo "-----------------------------------"
grep -n 'return.*["'"'"']<' app/items/routes.py || echo "None found"

echo -e "\n📌 LÖSUNG:"
echo "----------"
echo "Alle 'return' müssen so aussehen:"
echo "  return render_template('template.html', ...)"
echo "  return redirect(url_for('endpoint'))"
echo ""
echo "NIEMALS:"
echo "  return '<html>...'"
echo "  return some_html_string"
