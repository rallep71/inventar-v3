#!/usr/bin/env python3
"""
Inventar App v3.0 - Development Server
"""
import os
from app import create_app

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
