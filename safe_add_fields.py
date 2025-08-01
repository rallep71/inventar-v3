#!/usr/bin/env python3
"""
Safely add missing fields to items table
Run: python safe_add_fields.py
"""
from app import create_app, db
from sqlalchemy import text
import sys

def field_exists(field_name):
    """Check if a field exists in items table"""
    try:
        result = db.session.execute(text(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'items' 
            AND COLUMN_NAME = '{field_name}'
            AND TABLE_SCHEMA = DATABASE()
        """))
        return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking field {field_name}: {e}")
        return False

def add_field_if_missing(field_name, field_definition):
    """Add field if it doesn't exist"""
    if field_exists(field_name):
        print(f"✅ Field '{field_name}' already exists")
        return True
    
    try:
        db.session.execute(text(f"ALTER TABLE items ADD COLUMN {field_name} {field_definition}"))
        db.session.commit()
        print(f"✅ Added field '{field_name}'")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to add field '{field_name}': {e}")
        return False

def main():
    app = create_app()
    
    with app.app_context():
        print("🔧 Adding missing fields to items table...\n")
        
        # Define fields to add
        fields_to_add = {
            'purchase_price': 'DECIMAL(10,2) DEFAULT NULL',
            'room': 'VARCHAR(100) DEFAULT NULL',
            'shelf': 'VARCHAR(50) DEFAULT NULL',
            'compartment': 'VARCHAR(50) DEFAULT NULL',
            'model': 'VARCHAR(100) DEFAULT NULL',
            'notes': 'TEXT DEFAULT NULL',
            'serial_number': 'VARCHAR(100) DEFAULT NULL',
            'condition': "VARCHAR(50) DEFAULT 'Gut'",
            'team_id': 'INT DEFAULT NULL'
        }
        
        success_count = 0
        for field_name, field_def in fields_to_add.items():
            if add_field_if_missing(field_name, field_def):
                success_count += 1
        
        print(f"\n📊 Summary: {success_count}/{len(fields_to_add)} fields processed")
        
        # Show current structure
        print("\n📋 Current items table structure:")
        try:
            result = db.session.execute(text("DESCRIBE items"))
            for row in result:
                print(f"  - {row[0]:<20} {row[1]}")
        except Exception as e:
            print(f"❌ Could not show table structure: {e}")
        
        print("\n✅ Database update complete!")

if __name__ == '__main__':
    main()
