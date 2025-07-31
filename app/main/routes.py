"""
Main routes - Homepage and general pages
"""
from flask import render_template
from app.main import main_bp


@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('main/home.html')


@main_bp.route('/test')
def test():
    """Test route"""
    return {
        "status": "OK",
        "message": "Inventar App v3 is running!",
        "htmx": "ready"
    }
