"""
💨 QUICK START GUIDE

Get up and running in 5 minutes!
"""

# 💨 Quick Start - TFG FastAPI Application

## 🚀 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
# Activate virtual environment (if needed)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 min)
```bash
# The .env file is already created with defaults
# For development, no changes needed!

# For production, update .env with:
# - DATABASE_URL (your database connection)
# - SECRET_KEY (generate a strong secret key)
```

### Step 3: Start the Server (1 min)
```bash
# Using make
make run

# OR using uvicorn directly
uvicorn main:app --reload
```

### Step 4: Test the API (1 min)
Visit: **http://localhost:8000/docs**

You'll see the interactive API documentation with all endpoints!

### Step 5: Register & Login (1 min)

**Register a new user:**
```json
POST /api/v1/usuarios
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Login:**
```
POST /api/v1/auth/login
username: user@example.com
password: securepassword123
```

**Copy the `access_token` and use it in the header:**
```
Authorization: Bearer <your-token-here>
```

## 📚 Key Endpoints

### 🔐 Authentication
```bash
POST /api/v1/auth/login
  Login with email and password
  Returns: JWT token
```

### 👤 Users
```bash
POST /api/v1/usuarios
  Register new user
  
GET /api/v1/usuarios/me
  Get your profile (requires token)
  
PUT /api/v1/usuarios/me
  Update your profile
  
DELETE /api/v1/usuarios/me
  Delete your account
  
GET /api/v1/usuarios/{email}
  Get any user's info (public)
  
DELETE /api/v1/usuarios/{email}
  Delete user (admin only)
```

### 🏥 System
```bash
GET /
  API information
  
GET /health
  Health check
```

## 🛠️ Useful Commands

```bash
# Format code
make format

# Check code quality
make lint

# Run tests
make test

# Run with coverage
make test-cov

# Clean cache files
make clean

# See all commands
make help
```

## 📖 Full Documentation

- **Main Guide**: `README.md`
- **Migration from Old Structure**: `MIGRATION_GUIDE.md`
- **Detailed Summary**: `RESTRUCTURING_SUMMARY.md`
- **Verification Checklist**: `CHECKLIST.md`

## 📁 Project Structure Overview

```
app/
├── config.py        ← Environment settings
├── db/              ← Database configuration
├── models/          ← Database models
├── schemas/         ← Data validation
├── security/        ← Authentication
└── api/v1/endpoints/
    ├── auth.py      ← Login
    └── usuarios.py  ← User management

main.py             ← Start here! Application entry point
```

## 🔑 Important Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (local) |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Tool configurations |
| `Makefile` | Development commands |
| `main.py` | Application entry point |

## 💡 Before You Start...

✅ Make sure you have Python 3.10+ installed:
```bash
python --version
```

✅ The `.env` file already has defaults for development

✅ Database will auto-create on first run (SQLite by default)

✅ Use Swagger UI (`/docs`) to test endpoints without tools

## 🚨 Troubleshooting

**Problem**: Import errors
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use a different port
uvicorn main:app --port 8001
```

**Problem**: Database errors
```bash
# Solution: Delete test.db and restart (it will recreate)
rm test.db
make run
```

**Problem**: Permission denied on Makefile
```bash
# Solution (macOS/Linux): Make it executable
chmod +x Makefile
make run
```

## 🎯 Next Steps

1. ✅ Get the server running (`make run`)
2. ✅ Open `/docs` in your browser
3. ✅ Try registering a user
4. ✅ Try logging in
5. ✅ Try accessing `/usuarios/me` with your token
6. ✅ Explore other endpoints

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Read `MIGRATION_GUIDE.md` to understand the structure
3. Review `CHECKLIST.md` to see what was done
4. Look at `tests/example_test.py` for code examples
5. Check docstrings in the code (they're comprehensive!)

## ✨ You're All Set!

Your FastAPI application is now ready for development. The project is:

- ✅ Well-organized
- ✅ Fully documented
- ✅ Production-ready
- ✅ Easy to test
- ✅ Scalable
- ✅ Secure

**Start here:** `uvicorn main:app --reload`

**Then go to:** http://localhost:8000/docs

**Happy coding!** 🚀
