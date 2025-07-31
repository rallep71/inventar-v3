#!/usr/bin/env python3
"""Initialize database with tables and test data"""
from app import create_app, db
from app.models import User, Category

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    print("✅ Tabellen erstellt!")
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@inventar.local',
            role='admin'
        )
        admin.set_password('admin123')  # ÄNDERN!
        db.session.add(admin)
        print("✅ Admin User erstellt (admin/admin123)")
    
    # Create basic categories
    categories = [
        ('Elektronik', 'ELK', 'bi-cpu'),
        ('Werkzeug', 'WZG', 'bi-tools'),
        ('Büro', 'BRO', 'bi-briefcase'),
        ('Haushalt', 'HSH', 'bi-house'),
    ]
    
    for name, prefix, icon in categories:
        if not Category.query.filter_by(prefix=prefix).first():
            cat = Category(name=name, prefix=prefix, icon=icon)
            db.session.add(cat)
    
    db.session.commit()
    print("✅ Basis-Daten erstellt!")
