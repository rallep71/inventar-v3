"""
Flask Extensions
Central place for all extensions to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Database
db = SQLAlchemy()

# Authentication
login_manager = LoginManager()
bcrypt = Bcrypt()

# Security
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"],
    storage_uri="memory://"
)
csrf = CSRFProtect()

# Login Manager Configuration
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melden Sie sich an, um diese Seite zu sehen.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'basic'
