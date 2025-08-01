#!/usr/bin/env python3
"""
Complete fix for all Inventar v3 issues
Run: python fix_all_problems.py
"""
import os
import sys
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_routes_imports():
    """Fix missing User import in routes.py"""
    routes_file = 'app/items/routes.py'
    
    print("🔧 Fixing imports in routes.py...")
    
    if not os.path.exists(routes_file):
        print(f"❌ {routes_file} not found!")
        return False
    
    # Backup original
    backup_path = f"{routes_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(routes_file, backup_path)
    print(f"📋 Backed up to: {backup_path}")
    
    # Read file
    with open(routes_file, 'r') as f:
        lines = f.readlines()
    
    # Find import section and ensure User is imported
    import_fixed = False
    for i, line in enumerate(lines):
        if 'from app.models import' in line:
            if 'User' not in line:
                # Add User to imports
                if line.strip().endswith('\n'):
                    lines[i] = line.rstrip() + ', User\n'
                else:
                    lines[i] = line.rstrip() + ', User\n'
                import_fixed = True
            break
    
    # If no models import found, add it
    if not import_fixed:
        for i, line in enumerate(lines):
            if line.startswith('from app.items import items'):
                lines.insert(i+1, 'from app.models import Item, Category, Log, User\n')
                import_fixed = True
                break
    
    # Write back
    if import_fixed:
        with open(routes_file, 'w') as f:
            f.writelines(lines)
        print("✅ Fixed imports!")
    else:
        print("⚠️  Imports might already be correct")
    
    return True

def fix_database_fields():
    """Add missing fields to database"""
    print("\n🔧 Fixing database fields...")
    
    try:
        from app import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Check current structure
            print("📊 Checking current table structure...")
            result = db.session.execute(text("DESCRIBE items"))
            existing_fields = {row[0] for row in result}
            
            # Fields we need
            required_fields = {
                'purchase_price': 'DECIMAL(10,2) DEFAULT NULL',
                'room': 'VARCHAR(100) DEFAULT NULL',
                'shelf': 'VARCHAR(50) DEFAULT NULL',
                'compartment': 'VARCHAR(50) DEFAULT NULL',
                'model': 'VARCHAR(100) DEFAULT NULL',
                'notes': 'TEXT',
                'serial_number': 'VARCHAR(100) DEFAULT NULL',
                'condition': "VARCHAR(50) DEFAULT 'Gut'",
                'team_id': 'INT DEFAULT NULL'
            }
            
            # Add missing fields
            for field_name, field_def in required_fields.items():
                if field_name not in existing_fields:
                    try:
                        print(f"  Adding {field_name}...")
                        db.session.execute(text(f"ALTER TABLE items ADD COLUMN {field_name} {field_def}"))
                        db.session.commit()
                        print(f"  ✅ Added {field_name}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"  ⚠️  Could not add {field_name}: {e}")
                else:
                    print(f"  ✅ {field_name} already exists")
            
            # Try to add foreign key constraint (if teams table exists)
            try:
                result = db.session.execute(text("SHOW TABLES LIKE 'teams'"))
                if result.fetchone():
                    # Check if constraint already exists
                    result = db.session.execute(text("""
                        SELECT CONSTRAINT_NAME 
                        FROM information_schema.KEY_COLUMN_USAGE 
                        WHERE TABLE_NAME = 'items' 
                        AND COLUMN_NAME = 'team_id' 
                        AND TABLE_SCHEMA = DATABASE()
                    """))
                    if not result.fetchone():
                        db.session.execute(text("""
                            ALTER TABLE items 
                            ADD CONSTRAINT fk_items_team 
                            FOREIGN KEY (team_id) REFERENCES teams(id) 
                            ON DELETE SET NULL
                        """))
                        db.session.commit()
                        print("  ✅ Added team_id foreign key")
                    else:
                        print("  ✅ team_id foreign key already exists")
            except Exception as e:
                print(f"  ℹ️  Skipping team_id constraint: {e}")
            
            print("\n✅ Database fields fixed!")
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def create_check_scripts():
    """Create utility scripts"""
    print("\n🔧 Creating utility scripts...")
    
    # Create check_db.py
    check_db_content = '''#!/usr/bin/env python3
"""Check database structure"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\\n📊 Items table structure:")
    print("-" * 50)
    try:
        result = db.session.execute(text("DESCRIBE items"))
        for row in result:
            print(f"{row[0]:<20} {row[1]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\\n📦 Item count:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM items"))
        count = result.scalar()
        print(f"Total items: {count}")
    except Exception as e:
        print(f"Error: {e}")
'''
    
    with open('check_db.py', 'w') as f:
        f.write(check_db_content)
    os.chmod('check_db.py', 0o755)
    print("✅ Created check_db.py")
    
    # Create test_item_creation.py
    test_content = '''#!/usr/bin/env python3
"""Test item creation"""
from app import create_app, db
from app.models import Item, Category, User

app = create_app()

with app.app_context():
    print("\\n🧪 Testing item creation...")
    
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
'''
    
    with open('test_item_creation.py', 'w') as f:
        f.write(test_content)
    os.chmod('test_item_creation.py', 0o755)
    print("✅ Created test_item_creation.py")

def create_uploads_directory():
    """Ensure uploads directory exists"""
    print("\n🔧 Creating uploads directory...")
    
    upload_dir = 'app/static/uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✅ Created {upload_dir}")
    else:
        print(f"✅ {upload_dir} already exists")
    
    # Set permissions
    try:
        os.chmod(upload_dir, 0o755)
        print("✅ Set directory permissions")
    except Exception as e:
        print(f"⚠️  Could not set permissions: {e}")

def main():
    print("🚀 Inventar v3 Complete Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app') or not os.path.exists('run.py'):
        print("❌ Error: Please run this script from the project root directory!")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    # Run all fixes
    steps = [
        ("Fixing routes imports", fix_routes_imports),
        ("Fixing database fields", fix_database_fields),
        ("Creating check scripts", create_check_scripts),
        ("Creating uploads directory", create_uploads_directory)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"Step: {step_name}")
        print('='*50)
        try:
            if step_func():
                success_count += 1
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"✅ Completed {success_count}/{len(steps)} steps successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python check_db.py")
    print("2. Run: python test_item_creation.py")
    print("3. Restart Flask: python run.py")
    print("4. Try creating an item again!")

if __name__ == '__main__':
    main()
