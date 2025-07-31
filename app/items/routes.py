"""
Items routes
"""
from app.items import items_bp


@items_bp.route('/')
def index():
    return "<h2>Items - Coming soon</h2>"
