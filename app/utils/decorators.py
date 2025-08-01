# app/utils/decorators.py
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
