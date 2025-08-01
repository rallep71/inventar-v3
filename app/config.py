# app/config.py
"""Application configuration"""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Base configuration"""
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'inventar.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Upload config
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 10485760))  # 10MB default
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 12))
    
    # Feature flags
    ENABLE_PWA = os.environ.get('ENABLE_PWA', 'True').lower() == 'true'
    ENABLE_API = os.environ.get('ENABLE_API', 'True').lower() == 'true'
    ENABLE_2FA = os.environ.get('ENABLE_2FA', 'True').lower() == 'true'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # App settings
    APP_NAME = 'Inventar v3'
    APP_VERSION = '3.0.0'
    
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
