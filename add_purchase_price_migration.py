#!/usr/bin/env python3
"""
Migration script to add purchase_price column to items table
Run: python add_purchase_price_migration.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text

def add_purchase_price_column():
    app = create_app()
    
    with app.app_context():
        print("🔄 Adding purchase_price column to items table...")
        
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'items' 
                AND COLUMN_NAME = 'purchase_price'
                AND TABLE_SCHEMA = DATABASE()
            """))
            
            if result.fetchone():
                print("✅ purchase_price column already exists")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE items 
                ADD COLUMN purchase_price DECIMAL(10,2) DEFAULT NULL
            """))
            db.session.commit()
            
            print("✅ purchase_price column added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            
            # Alternative approach if the above fails
            try:
                print("🔄 Trying alternative approach...")
                db.session.execute(text("""
                    ALTER TABLE items 
                    ADD purchase_price DECIMAL(10,2) DEFAULT NULL
                """))
                db.session.commit()
                print("✅ Column added with alternative approach!")
            except Exception as e2:
                print(f"❌ Alternative approach also failed: {e2}")
                
                # Check current table structure
                print("\n📊 Current table structure:")
                result = db.session.execute(text("DESCRIBE items"))
                for row in result:
                    print(f"  - {row[0]} ({row[1]})")

if __name__ == '__main__':
    add_purchase_price_column()
