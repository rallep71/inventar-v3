#!/usr/bin/env python3
"""
Migration script to update database for Items feature
Run: python migrate_items.py
"""
from app import create_app, db
from app.models import Team, Item, Category

app = create_app()

with app.app_context():
    print("🔄 Erstelle neue Tabellen...")
    
    # Create all tables
    db.create_all()
    
    # Check if we need to create a default team
    if Team.query.count() == 0:
        print("📦 Erstelle Standard-Team...")
        from app.models import User
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            default_team = Team(
                name="Standard Team",
                slug="standard",
                description="Standard Team für alle Benutzer",
                created_by=admin.id
            )
            db.session.add(default_team)
            
            # Add admin to team
            default_team.members.append(admin)
            db.session.commit()
            print("✅ Standard-Team erstellt!")
    
    # Create some sample categories if none exist
    if Category.query.count() == 0:
        print("🏷️ Erstelle Beispiel-Kategorien...")
        
        categories = [
            Category(name="Elektronik", prefix="ELK", icon="bi-cpu", color="primary"),
            Category(name="Werkzeug", prefix="WZG", icon="bi-tools", color="warning"),
            Category(name="Büromaterial", prefix="BRO", icon="bi-briefcase", color="info"),
            Category(name="Möbel", prefix="MBL", icon="bi-house", color="success"),
            Category(name="Fahrzeuge", prefix="FZG", icon="bi-car-front", color="danger"),
            Category(name="IT-Equipment", prefix="ITE", icon="bi-pc-display", color="secondary"),
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        print("✅ Kategorien erstellt!")
    
    print("\n✅ Migration abgeschlossen!")
    print("\nNächste Schritte:")
    print("1. Server starten: python run.py")
    print("2. Artikel anlegen unter /items/add")
    print("3. Weitere Kategorien unter /admin/categories verwalten")
