# migration_add_user_role.py
# Falls das role Feld fehlt, führe dieses Script aus

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Prüfe ob role Spalte existiert
        result = db.session.execute(text("SHOW COLUMNS FROM users LIKE 'role'"))
        if not result.fetchone():
            # Füge role Spalte hinzu
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(50) DEFAULT 'user' NOT NULL
            """))
            
            # Setze den ersten User als Admin
            db.session.execute(text("""
                UPDATE users 
                SET role = 'admin' 
                WHERE id = 1
            """))
            
            db.session.commit()
            print("✅ Role Feld wurde hinzugefügt!")
            print("✅ User mit ID 1 wurde als Admin gesetzt!")
        else:
            print("ℹ️  Role Feld existiert bereits")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        db.session.rollback()
