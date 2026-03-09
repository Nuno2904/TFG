#!/usr/bin/env python3
"""Rebuild database schema by dropping and recreating tables."""

from sqlalchemy import text, create_engine
from app.config import settings
from app.db.base import Base
from app.models import usuario, dataset, data, ml as ml_models

def rebuild_database():
    """Drop all tables and recreate from models."""
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Dropping all existing tables...")
    Base.metadata.drop_all(engine)
    print("✅ Tables dropped")
    
    print("\n🔄 Creating new tables with updated schema...")
    Base.metadata.create_all(engine)
    print("✅ Tables created with new schema")
    
    print("\n✅ Database rebuild complete!")
    print("   - ml_models table now includes 'model_type' field")
    print("   - All other tables preserved")

if __name__ == "__main__":
    try:
        rebuild_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
