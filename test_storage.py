#!/usr/bin/env python
"""Test script to verify storage configuration"""

from app.config import settings
import os

print("✅ Settings loaded")
print(f"   PROJECT_ROOT: {settings.PROJECT_ROOT}")
print(f"   MODEL_STORAGE_PATH: {settings.MODEL_STORAGE_PATH}")
print(f"   Exists: {settings.MODEL_STORAGE_PATH.exists()}")

if settings.MODEL_STORAGE_PATH.exists():
    contents = os.listdir(settings.MODEL_STORAGE_PATH)
    print(f"   Contents: {contents if contents else 'empty'}")
else:
    print("   ❌ Directory does not exist!")

print("\n✅ Test completed successfully!")
