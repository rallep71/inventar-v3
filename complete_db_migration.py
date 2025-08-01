#!/usr/bin/env python3
"""
Complete database migration for all missing columns
Run: python complete_db_migration.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text, inspect

def check_and_add_columns():
    app = create_app()
    
    with app.app_context():
        print("🔄 Checking and adding missing columns to items table...")
        
        # Get existing columns
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('items')]
        print(f"📊 Existing columns: {existing_columns}")
        
        # Define all columns that should exist with their SQL definitions
        required_columns = {
            'purchase_price': 'DECIMAL(10,2) DEFAULT NULL',
            'room': 'VARCHAR(100) DEFAULT NULL',
            'shelf': 'VARCHAR(50) DEFAULT NULL', 
            'compartment': 'VARCHAR(50) DEFAULT NULL',
            'brand': 'VARCHAR(100) DEFAULT NULL',
            'model': 'VARCHAR(100) DEFAULT NULL',
            'serial_number': 'VARCHAR(100) DEFAULT NULL',
            'color': 'VARCHAR(50) DEFAULT NULL',
            'size': 'VARCHAR(50) DEFAULT NULL',
            'condition': 'VARCHAR(50) DEFAULT "Gut"',
            'weight': 'DECIMAL(10,3) DEFAULT NULL',
            'dimensions': 'VARCHAR(100) DEFAULT NULL',
            'shipping_size': 'VARCHAR(50) DEFAULT NULL',
            'image_file': 'VARCHAR(200) DEFAULT NULL',
            'thumbnail_file': 'VARCHAR(200) DEFAULT NULL',
            'additional_images': 'TEXT DEFAULT NULL',
            'barcode': 'VARCHAR(100) DEFAULT NULL',
            'qr_code': 'VARCHAR(200) DEFAULT NULL',
            'notes': 'TEXT DEFAULT NULL',
            'tags': 'VARCHAR(500) DEFAULT NULL',
            'is_active': 'BOOLEAN DEFAULT TRUE',
            'is_sold': 'BOOLEAN DEFAULT FALSE',
            'is_borrowed': 'BOOLEAN DEFAULT FALSE',
            'borrowed_to': 'VARCHAR(100) DEFAULT NULL',
            'borrowed_date': 'DATETIME DEFAULT NULL',
            'sold_date': 'DATETIME DEFAULT NULL',
            'sold_price': 'DECIMAL(10,2) DEFAULT NULL',
            'last_inventoried': 'DATETIME DEFAULT NULL',
            'created_by': 'INTEGER DEFAULT NULL',
            'team_id': 'INTEGER DEFAULT NULL'
        }
        
        # Add missing columns
        added_columns = []
        failed_columns = []
        
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                try:
                    # Special handling for condition column (reserved word)
                    if column_name == 'condition':
                        query = f"ALTER TABLE items ADD COLUMN `{column_name}` {column_def}"
                    else:
                        query = f"ALTER TABLE items ADD COLUMN {column_name} {column_def}"
                    
                    db.session.execute(text(query))
                    db.session.commit()
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    db.session.rollback()
                    failed_columns.append((column_name, str(e)))
                    print(f"❌ Failed to add column {column_name}: {e}")
        
        # Add foreign key constraints
        print("\n🔗 Adding foreign key constraints...")
        
        constraints = [
            {
                'name': 'fk_items_created_by',
                'column': 'created_by',
                'references': 'users(id)',
                'on_delete': 'SET NULL'
            },
            {
                'name': 'fk_items_team_id',
                'column': 'team_id', 
                'references': 'teams(id)',
                'on_delete': 'SET NULL'
            }
        ]
        
        for constraint in constraints:
            try:
                # Check if constraint already exists
                result = db.session.execute(text(f"""
                    SELECT CONSTRAINT_NAME 
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                    WHERE TABLE_NAME = 'items' 
                    AND CONSTRAINT_NAME = '{constraint['name']}'
                    AND TABLE_SCHEMA = DATABASE()
                """))
                
                if not result.fetchone():
                    query = f"""
                        ALTER TABLE items 
                        ADD CONSTRAINT {constraint['name']} 
                        FOREIGN KEY ({constraint['column']}) 
                        REFERENCES {constraint['references']}
                        ON DELETE {constraint['on_delete']}
                    """
                    db.session.execute(text(query))
                    db.session.commit()
                    print(f"✅ Added constraint: {constraint['name']}")
                else:
                    print(f"ℹ️  Constraint already exists: {constraint['name']}")
            except Exception as e:
                db.session.rollback()
                print(f"⚠️  Failed to add constraint {constraint['name']}: {e}")
        
        # Summary
        print("\n📋 Migration Summary:")
        print(f"✅ Successfully added {len(added_columns)} columns: {', '.join(added_columns)}")
        if failed_columns:
            print(f"❌ Failed to add {len(failed_columns)} columns:")
            for col, err in failed_columns:
                print(f"   - {col}: {err}")
        
        # Show current table structure
        print("\n📊 Current table structure:")
        result = db.session.execute(text("DESCRIBE items"))
        for row in result:
            print(f"  - {row[0]} ({row[1]})")

if __name__ == '__main__':
    check_and_add_columns()
