#!/usr/bin/env python3
"""Test item creation"""
from app import create_app, db
from app.models import Item, Category, User

app = create_app()

with app.app_context():
    print("\n🧪 Testing item creation...")
    
    # Get admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("❌ No admin user found!")
        exit(1)
    
    # Get or create test category
    category = Category.query.first()
    if not category:
        print("❌ No categories found! Create one first.")
        exit(1)
    
    print(f"Using category: {category.name} ({category.prefix})")
    
    # Test creating an item
    try:
        test_item = Item(
            item_uid=f"{category.prefix}-TEST",
            name="Test Item",
            quantity=1,
            created_by=admin.id,
            condition="Gut",
            notes="Test item creation"
        )
        test_item.categories.append(category)
        
        db.session.add(test_item)
        db.session.commit()
        
        print("✅ Test item created successfully!")
        print(f"   ID: {test_item.item_uid}")
        
        # Clean up
        db.session.delete(test_item)
        db.session.commit()
        print("✅ Test item deleted")
        
    except Exception as e:
        print(f"❌ Failed to create item: {e}")
        db.session.rollback()
