# migration_add_category_hierarchy.py
# Führe dieses Script aus um die Datenbank zu aktualisieren

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Füge parent_id hinzu falls nicht vorhanden
        db.session.execute(text("""
            ALTER TABLE categories 
            ADD COLUMN IF NOT EXISTS parent_id INT,
            ADD COLUMN IF NOT EXISTS description TEXT,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            ADD CONSTRAINT fk_category_parent 
            FOREIGN KEY (parent_id) REFERENCES categories(id) 
            ON DELETE CASCADE
        """))
        
        db.session.commit()
        print("✅ Migration erfolgreich!")
        
    except Exception as e:
        print(f"❌ Fehler bei Migration: {e}")
        db.session.rollback()
