# app/__init__.py
import os
import logging
from datetime import timedelta
from flask import Flask, render_template, g, session
from app.config import Config
from app.extensions import init_extensions, db, limiter
from flask_wtf.csrf import generate_csrf


def create_app(config_class=Config):
    """Flask Application Factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Session Configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = app.config.get('SESSION_COOKIE_SECURE', False)
    
    # Initialize extensions
    init_extensions(app)
    
    # Make session permanent
    @app.before_request
    def before_request():
        session.permanent = True
        g.user = None
        
    # CSRF token in templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
    
    # Template globals
    @app.template_global()
    def is_htmx_request():
        from flask import request
        return request.headers.get('HX-Request') == 'true'
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/inventar.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Inventar App startup')
    
    # Register blueprints
    from app.main import main
    from app.auth import auth
    from app.items import items
    from app.admin import admin
    from app.api import api
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(items, url_prefix='/items')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(api, url_prefix='/api')
    
    # Rate limiting for auth routes
    limiter.limit("5 per minute")(auth)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if is_htmx_request():
            return render_template('errors/404_partial.html'), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if is_htmx_request():
            return render_template('errors/403_partial.html'), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if is_htmx_request():
            return render_template('errors/500_partial.html'), 500
        return render_template('errors/500.html'), 500
    
    # Create upload folder
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    return app
