#!/usr/bin/env python3
"""Migration: add low_data_warning column to ml_models table."""

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # PostgreSQL: ADD COLUMN IF NOT EXISTS
    # SQLite: no soporta IF NOT EXISTS en ALTER TABLE, usamos try/except
    try:
        conn.execute(text(
            "ALTER TABLE ml_models ADD COLUMN low_data_warning BOOLEAN DEFAULT FALSE"
        ))
        conn.commit()
        print("OK: columna low_data_warning añadida")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("OK: columna ya existía, no se hizo nada")
        else:
            raise
