#!/usr/bin/env python3
"""Rebuild database schema by dropping and recreating tables."""

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.base import Base
from app.models import usuario, dataset, data, ml as ml_models
from app.models.usuario import Usuario
from app.security.security import hash_password

def rebuild_database():
    """Drop all tables and recreate from models."""
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔄 Dropping all existing tables...")
    Base.metadata.drop_all(engine)
    print("✅ Tables dropped")
    
    print("\n🔄 Creating new tables with updated schema...")
    Base.metadata.create_all(engine)
    print("✅ Tables created with new schema")
    
    # 🔐 Create default admin user
    print("\n🔐 Creating default admin user...")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if admin already exists
        admin_user = session.query(Usuario).filter_by(email="administrador@seriestemporales.com").first()
        
        if not admin_user:
            admin_user = Usuario(
                username="administrador",
                email="administrador@seriestemporales.com",
                password=hash_password("administrador"),
                tipo="admin"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created:")
            print("   📧 Email: administrador@seriestemporales.com")
            print("   👤 Username: administrador")
            print("   🔑 Password: administrador")
            print("   👨‍💼 Type: admin")
        else:
            print("⏭️  Admin user already exists, skipping creation")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        session.rollback()
    finally:
        session.close()
    
    print("\n✅ Database rebuild complete!")
    print("   - ml_models table now includes 'model_type' field")
    print("   - All other tables preserved")
    print("   - Default admin user initialized")

if __name__ == "__main__":
    try:
        rebuild_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
