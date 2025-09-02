#!/usr/bin/env python3
"""
Quick database fix script for WeatherGuard Harvest.
This script will reset the database to match the current models.
"""

import os
import sys

def fix_database():
    """Fix the database schema mismatch."""
    print("🔧 Fixing database schema mismatch...")
    
    # Check if database exists
    db_path = 'instance/users.db'
    if os.path.exists(db_path):
        try:
            # Remove the problematic database
            os.remove(db_path)
            print("✓ Removed old database file")
        except Exception as e:
            print(f"✗ Error removing database: {e}")
            return False
    else:
        print("ℹ️  No existing database found")
    
    # Import and initialize the app
    try:
        from app import app, db
        
        with app.app_context():
            # Create new database with current schema
            db.create_all()
            print("✓ Created new database with current schema")
            
        print("✓ Database fixed successfully!")
        print("\nYou can now run the application:")
        print("python app.py")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("WeatherGuard Harvest - Database Fix Tool")
    print("=" * 40)
    
    if fix_database():
        print("\n🎉 Database issue resolved!")
    else:
        print("\n❌ Failed to fix database. Please check the error messages above.")
        sys.exit(1)
