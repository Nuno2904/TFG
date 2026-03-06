"""
📂 Project Paths Configuration

Centralized management of absolute file system paths.
Ensures all storage paths are resolved relative to the project root.
"""

from pathlib import Path

# 🎯 Project Root (TFG folder)
# This file is at: .../TFG/app/paths.py
# So parent.parent gets us to TFG/
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 📂 Storage Paths (All absolute paths)
STORAGE_DIR = PROJECT_ROOT / "storage"
MODELS_DIR = STORAGE_DIR / "models"

# 🔧 Auto-create directories on import
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Debug info
if __name__ == "__main__":
    print(f"📍 PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"📂 STORAGE_DIR: {STORAGE_DIR}")
    print(f"🤖 MODELS_DIR: {MODELS_DIR}")
    print(f"✅ All directories exist")
