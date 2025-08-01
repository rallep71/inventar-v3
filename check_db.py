#!/usr/bin/env python3
"""Check database structure"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n📊 Items table structure:")
    print("-" * 50)
    try:
        result = db.session.execute(text("DESCRIBE items"))
        for row in result:
            print(f"{row[0]:<20} {row[1]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n📦 Item count:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM items"))
        count = result.scalar()
        print(f"Total items: {count}")
    except Exception as e:
        print(f"Error: {e}")
