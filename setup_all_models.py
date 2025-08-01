#!/usr/bin/env python3
"""
setup_all_models.py - Installiert alle Model-Dateien auf einmal
"""
import os

def create_file(path, content):
    """Create a file with content"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {path}")

def main():
    print("🚀 Setting up all model files...\n")
    
    # User Model
    create_file('app/models/user.py', '''# app/models/user.py
"""User model"""
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    
    # 2FA fields
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String(32), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    created_items = db.relationship('Item', foreign_keys='Item.created_by', back_populates='creator', lazy='dynamic')
    logs = db.relationship('Log', backref='user', lazy='dynamic')
    created_teams = db.relationship('Team', foreign_keys='Team.created_by', back_populates='creator', lazy='dynamic')
    # teams relationship is created by backref in Team model via secondary table
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'
''')

    # Category Model
    create_file('app/models/category.py', '''# app/models/category.py
"""Category model"""
from app.extensions import db


class Category(db.Model):
    """Category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Bootstrap icon class
    color = db.Column(db.String(20))  # For UI theming
    
    # Hierarchical categories
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    children = db.relationship('Category',
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    # Ordering
    sort_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Category {self.name} ({self.prefix})>'
    
    def get_full_path(self):
        """Get full category path (Parent > Child)"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
''')

    # Log Model
    create_file('app/models/log.py', '''# app/models/log.py
"""Log model for activity tracking"""
from datetime import datetime
from app.extensions import db


class Log(db.Model):
    """Activity log model"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    
    # Log levels
    level = db.Column(db.String(20), default='info')  # info, warning, error
    
    def __repr__(self):
        return f'<Log {self.action} by User {self.user_id}>'
''')

    # Models __init__.py
    create_file('app/models/__init__.py', '''"""Import all models"""
from app.models.user import User
from app.models.item import Item
from app.models.category import Category
from app.models.log import Log
from app.models.team import Team

__all__ = ["User", "Item", "Category", "Log", "Team"]
''')

    # Utils decorators
    create_file('app/utils/decorators.py', '''# app/utils/decorators.py
"""Custom decorators for access control"""
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from app.models.team import Team


def admin_required(f):
    """Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def team_required(f):
    """Require user to be part of at least one team"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.teams.count() and not current_user.is_admin():
            flash('Sie müssen einem Team angehören, um auf diese Funktion zuzugreifen.', 'warning')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def team_member_required(team_id_param='team_id'):
    """Require user to be member of specific team"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            team_id = kwargs.get(team_id_param)
            if not team_id:
                abort(400)
            
            # Admin can access all teams
            if current_user.is_admin():
                return f(*args, **kwargs)
            
            # Check if user is member of this team
            team = Team.query.get_or_404(team_id)
            if current_user not in team.members:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
''')

    # Utils __init__.py
    create_file('app/utils/__init__.py', '')

    # Toast utilities (falls nicht vorhanden)
    create_file('app/utils/toast.py', '''# app/utils/toast.py
"""Toast utilities for HTMX responses"""
from flask import make_response, render_template_string


def htmx_toast(response, message, category='info'):
    """Add HTMX toast trigger to response"""
    response.headers['HX-Trigger'] = f'{{"showToast": {{"message": "{message}", "category": "{category}"}}}}'
    return response


def toast_response(message, category='info', status=200):
    """Return empty response with toast trigger"""
    response = make_response('', status)
    return htmx_toast(response, message, category)


def toast_redirect(url, message, category='info'):
    """Return redirect response with toast"""
    response = make_response('', 200)
    response.headers['HX-Redirect'] = url
    return htmx_toast(response, message, category)
''')

    print("\n✅ All model files created successfully!")
    print("\n📋 Created files:")
    print("  - app/models/user.py")
    print("  - app/models/category.py") 
    print("  - app/models/log.py")
    print("  - app/models/__init__.py")
    print("  - app/utils/decorators.py")
    print("  - app/utils/toast.py")
    print("  - app/utils/__init__.py")
    
    print("\n⚠️  Sie müssen noch folgende Dateien aus den Artifacts kopieren:")
    print("  - app/models/item.py (Item Model - Erweitert)")
    print("  - app/models/team.py (Team Model)")
    
    print("\n🚀 Next steps:")
    print("1. Kopieren Sie item.py und team.py aus den Artifacts")
    print("2. Cache löschen: find . -name '*.pyc' -delete")
    print("3. python migrate_items.py")
    print("4. python run.py")

if __name__ == "__main__":
    main()
