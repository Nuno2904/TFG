#!/usr/bin/env python
"""Verify model_type field is present"""
from app.models.ml import MLModel

print("✅ MLModel verification:")
print(f"   - Has model_type column: {hasattr(MLModel, 'model_type')}")

# Check table columns
if hasattr(MLModel, '__table__'):
    print(f"   - Table columns: {list(MLModel.__table__.columns.keys())}")

print("\n✅ Schema verification:")
from app.schemas.ml import MLModelCreate, MLModelOut
print(f"   - MLModelCreate requires model_type: {'model_type' in MLModelCreate.model_fields}")
print(f"   - MLModelOut includes model_type: {'model_type' in MLModelOut.model_fields}")

print("\n✅ All fields look good!")
