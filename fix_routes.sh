#!/bin/bash

# Fix Routes Script for Inventar v3
echo "🔧 Fixing routes for Inventar v3..."

# Backup existing files
echo "📦 Creating backups..."
cp app/items/routes.py app/items/routes.py.backup 2>/dev/null
cp app/main/routes.py app/main/routes.py.backup 2>/dev/null

# Create main routes fix
echo "📝 Fixing main/routes.py..."
cat > app/main/routes.py << 'EOF'
# app/main/routes.py
"""Main blueprint routes"""
from flask import redirect, url_for
from flask_login import login_required
from app.main import main

@main.route('/')
@login_required
def index():
    """Redirect to items index"""
    return redirect(url_for('items.index'))
EOF

echo "✅ Main routes fixed!"

# Create directories if they don't exist
mkdir -p app/templates/items/partials

echo "🎉 Routes fix complete!"
echo ""
echo "⚠️  IMPORTANT: You still need to:"
echo "1. Update app/items/routes.py with the full routes code"
echo "2. Add the missing templates (scan.html, detail.html)"
echo "3. Restart your Flask application"
echo ""
echo "Run: python run.py"
