"""
Admin routes
"""
from app.admin import admin_bp


@admin_bp.route('/')
def index():
    return "<h2>Admin - Coming soon</h2>"
