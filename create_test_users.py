#!/usr/bin/env python3
# create_test_users.py - Run from project root: python create_test_users.py

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User
import pyotp


def create_test_users():
    """Create test users for development"""
    app = create_app()
    
    with app.app_context():
        # Check if users already exist
        if User.query.filter_by(username='admin').first():
            print("⚠️  Test users already exist!")
            return
        
        # Create admin user (no 2FA)
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Admin user created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   2FA: Disabled")
        
        # Create normal user (with 2FA)
        user = User(
            username='user',
            email='user@example.com',
            role='user'
        )
        user.set_password('user123')
        user.is_2fa_enabled = True
        user.generate_totp_secret()
        db.session.add(user)
        
        # Create another user without 2FA
        user2 = User(
            username='test',
            email='test@example.com',
            role='user'
        )
        user2.set_password('test123')
        db.session.add(user2)
        
        # Commit all users
        db.session.commit()
        
        print("\n✅ Normal user created:")
        print("   Username: user")
        print("   Password: user123")
        print("   2FA: Enabled")
        print("\n📱 2FA QR Code URL:")
        print(f"   {user.get_totp_uri()}")
        print("\n   Use Google Authenticator or similar app to scan")
        
        print("\n✅ Test user created:")
        print("   Username: test")
        print("   Password: test123")
        print("   2FA: Disabled")
        
        print("\n🎉 All test users created successfully!")


if __name__ == '__main__':
    create_test_users()
