"""
Database Initialization Script

This script will:
1. Drop all existing tables (if any)
2. Recreate all tables with the latest schema (including crop_type)
3. Initialize the database for fresh start

WARNING: This will delete all existing data!
"""

import asyncio
import sys
sys.path.insert(0, '.')

from database import engine, Base, drop_tables, create_tables
from models.user import User
from models.farm import Farm


async def init_database():
    """Initialize database with fresh schema"""
    print("🗄️  Initializing database...")
    
    try:
        # Drop all existing tables
        print("   Dropping existing tables...")
        await drop_tables()
        print("   ✅ Tables dropped")
        
        # Create all tables with new schema
        print("   Creating tables with new schema...")
        await create_tables()
        print("   ✅ Tables created successfully")
        
        print("\n✨ Database initialized successfully!")
        print("   All tables have been created with the latest schema.")
        print("   The 'farms' table now includes the 'crop_type' field.")
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete all existing data!")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        asyncio.run(init_database())
    else:
        print("\n❌ Database initialization cancelled.")
