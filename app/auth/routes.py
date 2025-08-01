# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import LoginForm
from app.models.user import User
from app.extensions import db
from datetime import datetime
from app.utils.toast import htmx_toast, toast_redirect

auth = Blueprint('auth', __name__)

def is_htmx_request():
    return request.headers.get('HX-Request') == 'true'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if is_htmx_request():
            response = make_response()
            response.headers['HX-Redirect'] = url_for('items.index')
            return response
        return redirect(url_for('items.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Login successful
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if is_htmx_request():
                return toast_redirect(url_for('items.index'), 
                                    f'Willkommen zurück, {user.username}!', 
                                    'success')
            
            return redirect(url_for('items.index'))
        
        # Login failed
        if is_htmx_request():
            form.username.errors.append('Ungültige Anmeldedaten')
            return render_template('auth/partials/login_form.html', form=form)
    
    # GET request
    if is_htmx_request():
        return render_template('auth/partials/login_form.html', form=form)
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    
    if is_htmx_request():
        return toast_redirect(url_for('auth.login'), 
                            'Sie wurden erfolgreich abgemeldet', 
                            'info')
    
    return redirect(url_for('auth.login'))
