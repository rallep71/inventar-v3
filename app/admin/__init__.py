# app/admin/__init__.py
"""Admin panel blueprint"""
from flask import Blueprint

admin = Blueprint('admin', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.admin import routes
