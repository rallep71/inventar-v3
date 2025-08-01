# app/admin/__init__.py
"""Admin panel blueprint"""
from flask import Blueprint

admin = Blueprint('admin', __name__)

# Temporär - wird später implementiert
@admin.route('/')
def index():
    return "Admin Panel - Coming Soon"
