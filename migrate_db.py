#!/usr/bin/env python3
"""
Database migration script for WeatherGuard Harvest.
This script helps update the database schema when models change.
"""

import os
import sqlite3
from app import app, db

def backup_database():
    """Create a backup of the current database."""
    if os.path.exists('instance/users.db'):
        import shutil
        backup_name = f'instance/users_backup_{int(time.time())}.db'
        shutil.copy2('instance/users.db', backup_name)
        print(f"✓ Database backed up to {backup_name}")
        return backup_name
    return None

def check_database_schema():
    """Check the current database schema."""
    with app.app_context():
        try:
            # Get table info
            result = db.session.execute("PRAGMA table_info(user)")
            columns = result.fetchall()
            
            print("Current database schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")
            
            return columns
        except Exception as e:
            print(f"Error checking schema: {e}")
            return None

def migrate_database():
    """Migrate the database to match current models."""
    print("Starting database migration...")
    
    # Backup current database
    backup_file = backup_database()
    
    with app.app_context():
        try:
            # Drop existing tables and recreate
            db.drop_all()
            print("✓ Dropped existing tables")
            
            # Create new tables with current schema
            db.create_all()
            print("✓ Created new tables with current schema")
            
            print("✓ Database migration completed successfully!")
            if backup_file:
                print(f"  Previous database backed up to: {backup_file}")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            if backup_file:
                print(f"  You can restore from backup: {backup_file}")
            return False
    
    return True

def reset_database():
    """Reset the database completely (WARNING: This will delete all data)."""
    response = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        with app.app_context():
            try:
                db.drop_all()
                db.create_all()
                print("✓ Database reset completed")
                return True
            except Exception as e:
                print(f"✗ Reset failed: {e}")
                return False
    else:
        print("Database reset cancelled.")
        return False

if __name__ == "__main__":
    import time
    
    print("WeatherGuard Harvest - Database Migration Tool")
    print("=" * 50)
    
    print("\nOptions:")
    print("1. Check current schema")
    print("2. Migrate database (recommended)")
    print("3. Reset database (WARNING: deletes all data)")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == '1':
        check_database_schema()
    elif choice == '2':
        migrate_database()
    elif choice == '3':
        reset_database()
    elif choice == '4':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")
