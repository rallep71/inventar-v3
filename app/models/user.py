# app/models/user.py
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
