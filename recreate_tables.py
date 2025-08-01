#!/usr/bin/env python3
"""
Recreate all tables - USE WITH CAUTION! This will delete all data!
Run: python recreate_tables.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Item, Category, Team, Log

def recreate_all_tables():
    app = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
        print("⚠️  This should only be used in development!")
        
        response = input("\nAre you sure you want to continue? Type 'yes' to proceed: ")
        
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        
        print("\n🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped.")
        
        print("\n🔨 Creating all tables...")
        db.create_all()
        print("✅ All tables created.")
        
        # Create default admin user
        print("\n👤 Creating default admin user...")
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('admin123')  # Change this!
        db.session.add(admin)
        db.session.flush()
        
        # Create default team
        print("📦 Creating default team...")
        default_team = Team(
            name="Standard Team",
            slug="standard",
            description="Standard Team für alle Benutzer",
            created_by=admin.id
        )
        db.session.add(default_team)
        db.session.flush()
        
        # Add admin to team
        default_team.add_member(admin, role='admin')
        
        # Create some default categories
        print("🏷️  Creating default categories...")
        categories = [
            {'name': 'Elektronik', 'prefix': 'EL', 'color': '#007bff'},
            {'name': 'Möbel', 'prefix': 'MB', 'color': '#28a745'},
            {'name': 'Werkzeug', 'prefix': 'WZ', 'color': '#ffc107'},
            {'name': 'Bürobedarf', 'prefix': 'BB', 'color': '#17a2b8'},
            {'name': 'Sonstiges', 'prefix': 'SO', 'color': '#6c757d'}
        ]
        
        for cat_data in categories:
            category = Category(
                name=cat_data['name'],
                prefix=cat_data['prefix'],
                color=cat_data['color']
            )
            db.session.add(category)
        
        # Commit all changes
        db.session.commit()
        
        print("\n✅ Database recreated successfully!")
        print("\n📌 Default credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Please change the admin password immediately!")
        
        # Show table structure
        from sqlalchemy import text
        print("\n📊 Items table structure:")
        result = db.session.execute(text("DESCRIBE items"))
        for row in result:
            print(f"  - {row[0]} ({row[1]})")

if __name__ == '__main__':
    recreate_all_tables()
