"""
Inventar App v3.0 - Modern Inventory Management
Built with Flask, HTMX, and Alpine.js
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_talisman import Talisman

from app.config import config
from app.extensions import db, login_manager, bcrypt, limiter, csrf


def create_app(config_name=None):
    """Create Flask application using factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    register_error_handlers(app)
    
    # Setup logging
    configure_logging(app)
    
    # Create upload directory
    create_upload_directory(app)
    
    # Add template globals
    register_template_filters(app)
    
    # Security headers with Talisman
    if not app.debug and not app.testing:
        init_security_headers(app)
    
    return app


def init_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    
    # Setup user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()


def register_blueprints(app):
    """Register all blueprints"""
    # Import here to avoid circular imports
    from app.main import main_bp
    from app.auth import auth_bp
    from app.items import items_bp
    from app.admin import admin_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(items_bp, url_prefix='/items')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    if app.config.get('ENABLE_API'):
        app.register_blueprint(api_bp, url_prefix='/api/v1')


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            'logs/inventar.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Inventar App v3 startup')


def create_upload_directory(app):
    """Create upload directory if it doesn't exist"""
    upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)


def register_template_filters(app):
    """Register custom template filters and globals"""
    @app.template_global()
    def is_htmx_request():
        """Check if request is from HTMX"""
        from flask import request
        return request.headers.get('HX-Request') == 'true'
    
    @app.template_filter('datetime')
    def datetime_filter(date):
        """Format datetime for display"""
        if date:
            return date.strftime('%d.%m.%Y %H:%M')
        return ''
    
    @app.context_processor
    def inject_config():
        """Inject configuration into templates"""
        return {
            'ENABLE_PWA': app.config.get('ENABLE_PWA'),
            'ENABLE_2FA': app.config.get('ENABLE_2FA'),
            'APP_VERSION': '3.0.0'
        }


def init_security_headers(app):
    """Initialize security headers with Talisman"""
    csp = {
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # For HTMX
            "https://unpkg.com",  # HTMX CDN
            "https://cdn.jsdelivr.net"  # Alpine.js CDN
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # For inline styles
            "https://cdn.jsdelivr.net"  # Bootstrap CDN
        ],
        'img-src': ["'self'", "data:", "blob:"],
        'connect-src': ["'self'"],
        'font-src': ["'self'", "data:"],
        'frame-src': ["'none'"],
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"]
    }
    
    Talisman(app,
        force_https=False,  # Set True in production
        strict_transport_security=True,
        content_security_policy=csp
    )
