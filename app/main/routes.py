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
