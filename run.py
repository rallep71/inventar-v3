#!/usr/bin/env python3
"""
Inventar App v3 - Run Script
Usage: python run.py
"""
import os
from app import create_app, db
from app.models import User, Item, Category, Log, Team

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'Item': Item,
        'Category': Category,
        'Log': Log,
        'Team': Team
    }


if __name__ == '__main__':
    # Development server configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"""
    🚀 Inventar App v3.0 
    🌐 Running on http://{host}:{port}
    🔧 Debug mode: {'ON' if debug else 'OFF'}
    📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}
    
    Press CTRL+C to quit
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
