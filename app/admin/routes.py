# app/admin/routes.py
"""Admin panel routes"""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.models import User, Item, Category, Team, Log
from app.extensions import db

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Collect statistics
    stats = {
        'total_items': Item.query.count(),
        'total_users': User.query.count(),
        'total_categories': Category.query.count(),
        'total_teams': Team.query.count(),
        'recent_logs': Log.query.order_by(Log.timestamp.desc()).limit(10).all(),
        'low_stock_items': Item.query.filter(Item.quantity <= 5).count(),
        'sold_items': Item.query.filter(Item.is_sold == True).count(),
        'borrowed_items': Item.query.filter(Item.is_borrowed == True).count()
    }
    
    return render_template('admin/dashboard.html', stats=stats)


@admin.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin.route('/teams')
@login_required
@admin_required
def teams():
    """Team management"""
    all_teams = Team.query.order_by(Team.created_at.desc()).all()
    return render_template('admin/teams.html', teams=all_teams)


@admin.route('/categories')
@login_required
@admin_required
def categories():
    """Category management"""
    all_categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=all_categories)


@admin.route('/logs')
@login_required
@admin_required
def logs():
    """System logs"""
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)


@admin.route('/system')
@login_required
@admin_required
def system():
    """System information and tools"""
    # Get database info
    from app import create_app
    app = create_app()
    
    system_info = {
        'database_url': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite',
        'flask_version': '3.0.0',
        'app_version': app.config.get('APP_VERSION', '3.0.0'),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_upload_size': app.config['MAX_CONTENT_LENGTH'] // 1024 // 1024,  # MB
    }
    
    return render_template('admin/system.html', system_info=system_info)
