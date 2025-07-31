#!/bin/bash

# Inventar v3 - Project Setup Script (ohne Git)

echo "🚀 Setting up Inventar App v3.0..."

# Create main directories
echo "📁 Creating directory structure..."

# Main app directory
mkdir -p app/{models,auth,main,items,admin,api,static,templates}

# Static subdirectories
mkdir -p app/static/{src/{js/{modules,vendor},css/{components,vendor}},dist,images,uploads}

# Template subdirectories
mkdir -p app/templates/{layout,components,partials,auth,items,admin,errors}

# Other directories
mkdir -p {migrations,tests/{unit,integration,fixtures},docs}

# Create __init__.py files
echo "📝 Creating __init__.py files..."
touch app/__init__.py
touch app/models/__init__.py
touch app/auth/__init__.py
touch app/main/__init__.py
touch app/items/__init__.py
touch app/admin/__init__.py
touch app/api/__init__.py

# Create empty test files
touch tests/__init__.py
touch tests/conftest.py

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📋 Created .env file from .env.example"
fi

# Make uploads directory writable
chmod 755 app/static/uploads

echo "✅ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Configure your .env file"
echo "4. Run: python run.py"
