#!/usr/bin/env python3
"""
Migration script to update database for Items feature
Run: python migrate_items.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db

# Importiere die Models einzeln um Zirkularität zu vermeiden
app = create_app()

with app.app_context():
    print("🔄 Erstelle neue Tabellen...")
    
    # Drop und recreate all tables (nur für Entwicklung!)
    # In Produktion würde man Alembic migrations verwenden
    try:
        # Versuche zuerst die Tabellen zu erstellen
        db.create_all()
        print("✅ Tabellen erstellt!")
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Tabellen: {e}")
        print("Versuche Tabellen neu zu erstellen...")
        
        # Optional: Drop all tables and recreate (NUR IN ENTWICKLUNG!)
        response = input("Sollen alle Tabellen gelöscht und neu erstellt werden? (j/n): ")
        if response.lower() == 'j':
            db.drop_all()
            db.create_all()
            print("✅ Tabellen neu erstellt!")
        else:
            print("❌ Migration abgebrochen")
            sys.exit(1)
    
    # Importiere Models nach Tabellenerstellung
    from app.models import Team, User, Category, Item
    
    # Check if we need to create a default team
    if Team.query.count() == 0:
        print("📦 Erstelle Standard-Team...")
        
        # Finde oder erstelle Admin User
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            print("👤 Erstelle Admin User...")
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')  # Ändern Sie dies!
            db.session.add(admin)
            db.session.flush()  # Damit wir die ID bekommen
        
        default_team = Team(
            name="Standard Team",
            slug="standard",
            description="Standard Team für alle Benutzer",
            created_by=admin.id
        )
        db.session.add(default_team)
        db.session.commit()
        
        # Add admin to team
        default_team.add_member(admin, role='admin')
        db.session.commit()
        print("✅ Standard-Team erstellt!")
    
    # Create some sample categories if none exist
    if Category.query.count() == 0:
        print("🏷️ Erstelle Beispiel-Kategorien...")
        
        categories = [
            Category(
                name="Elektronik", 
                prefix="ELK", 
                icon="bi-cpu", 
                color="primary",
                description="Elektronische Geräte und Komponenten"
            ),
            Category(
                name="Werkzeug", 
                prefix="WZG", 
                icon="bi-tools", 
                color="warning",
                description="Werkzeuge und Handwerkszeug"
            ),
            Category(
                name="Büromaterial", 
                prefix="BRO", 
                icon="bi-briefcase", 
                color="info",
                description="Bürobedarf und Schreibwaren"
            ),
            Category(
                name="Möbel", 
                prefix="MBL", 
                icon="bi-house", 
                color="success",
                description="Möbel und Einrichtungsgegenstände"
            ),
            Category(
                name="Fahrzeuge", 
                prefix="FZG", 
                icon="bi-car-front", 
                color="danger",
                description="Fahrzeuge und Fahrzeugzubehör"
            ),
            Category(
                name="IT-Equipment", 
                prefix="ITE", 
                icon="bi-pc-display", 
                color="secondary",
                description="Computer, Server und IT-Zubehör"
            ),
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        print("✅ Kategorien erstellt!")
    
    print("\n✅ Migration abgeschlossen!")
    print("\nNächste Schritte:")
    print("1. Server starten: python run.py")
    print("2. Als admin einloggen (admin/admin123)")
    print("3. Passwort ändern unter /auth/profile")
    print("4. Artikel anlegen unter /items/add")
    print("5. Weitere Kategorien unter /admin/categories verwalten")
