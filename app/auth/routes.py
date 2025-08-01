# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import LoginForm, TwoFactorForm
from app.models.user import User
from app.extensions import db
import pyotp

auth = Blueprint('auth', __name__)

def is_htmx_request():
    """Check if request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('items.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Check if 2FA is enabled
            if user.is_2fa_enabled:
                # Store user in session for 2FA step
                session['pending_user_id'] = user.id
                session['remember'] = form.remember.data
                
                if is_htmx_request():
                    return render_template('auth/partials/2fa_form.html')
                return redirect(url_for('auth.verify_2fa'))
