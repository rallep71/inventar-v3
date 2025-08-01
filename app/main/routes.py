# app/main/routes.py
"""Main routes for homepage and general pages"""
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main
from app.models import Item, Category


@main.route('/')
@main.route('/index')
def index():
    """Homepage - redirect to items if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('items.index'))
    return render_template('index.html', title='Willkommen')


@main.route('/about')
def about():
    """About page"""
    return render_template('about.html', title='Über uns')


@main.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}, 200
