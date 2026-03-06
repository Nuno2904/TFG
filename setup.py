#!/usr/bin/env python
"""
🛠️ Setup Script

Run this script to set up the development environment.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run setup tasks."""
    print("=" * 70)
    print("🚀 Setting up TFG FastAPI Application")
    print("=" * 70)
    
    # Get project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 1️⃣ Check Python version
    print("\n1️⃣ Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split(' ')[0]} OK")
    
    # 2️⃣ Check if venv exists
    print("\n2️⃣ Checking virtual environment...")
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment ready")
    
    # 3️⃣ Upgrade pip
    print("\n3️⃣ Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # 4️⃣ Install dependencies
    print("\n4️⃣ Installing dependencies...")
    if (project_root / "requirements.txt").exists():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
    print("✅ Dependencies installed")
    
    # 5️⃣ Create .env if not exists
    print("\n5️⃣ Checking environment file...")
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env from template...")
        with open(env_example) as f:
            content = f.read()
        with open(env_file, "w") as f:
            f.write(content)
        print("✅ .env created (update with your values)")
    elif env_file.exists():
        print("✅ .env file already exists")
    
    print("\n" + "=" * 70)
    print("✅ Setup complete!")
    print("=" * 70)
    print("\n📖 Next steps:")
    print("1. Update .env with your database and secret key")
    print("2. Run: uvicorn main:app --reload")
    print("3. Visit: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
