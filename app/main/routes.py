# app/main/routes.py
"""Main blueprint routes"""
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main


@main.route('/')
def home():
    """Homepage - redirect to items if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('items.index'))
    return redirect(url_for('auth.login'))


@main.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')
