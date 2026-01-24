# Complete Setup Guide - AI Life Admin Assistant

## 🚀 Quick Start (3 Steps)

### Step 1: Start Database (REQUIRED for Sign Up/Login)
```powershell
.\start_database.ps1
```
**OR** if you have Docker:
```powershell
docker compose up -d postgres
```

### Step 2: Start Backend
```powershell
.\restart_backend.ps1
```
Wait for: "Uvicorn running on http://0.0.0.0:8000"

### Step 3: Start Frontend
```powershell
cd frontend
npm install  # First time only
npm run dev
```

**OR** start both at once:
```powershell
.\start_all.ps1
```

---

## ✅ What You Need to Do

### 1. **PostgreSQL Database** ⚠️ REQUIRED
**Why:** Sign up and login won't work without it

**Options:**
- **Option A: Docker (Easiest)**
  ```powershell
  .\start_database.ps1
  ```
  
- **Option B: Install PostgreSQL Locally**
  1. Download: https://www.postgresql.org/download/windows/
  2. Install with default settings
  3. Create database: `ailifeadmin`
  4. Update `.env` if needed

**Verify it's running:**
- Port 5432 should be open
- Try sign up at http://localhost:8000/api/docs

### 2. **Backend Server** ✅ REQUIRED
**Status:** Should be running in a PowerShell window

**If not running:**
```powershell
.\restart_backend.ps1
```

**Check:** http://localhost:8000/api/health

### 3. **Frontend Server** ✅ REQUIRED
**Status:** Should be running in a PowerShell window

**If not running:**
```powershell
cd frontend
npm run dev
```

**Check:** http://localhost:5173

### 4. **Redis** ⚠️ OPTIONAL
**Why:** Needed for rate limiting and caching

**Start:**
```powershell
docker compose up -d redis
```

**Note:** App works without it, but some features may be limited

### 5. **AI Features** ⚠️ OPTIONAL
**Why:** For document classification, task extraction, daily plans

**Setup:**
1. Install Ollama: https://ollama.ai
2. Start: `ollama serve`
3. Download model: `ollama pull llama3:8b`
4. Install spaCy model:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m spacy download en_core_web_sm
   ```

### 6. **AWS S3** ⚠️ OPTIONAL
**Why:** For document storage

**Setup:**
1. Create AWS account
2. Create S3 bucket
3. Get access keys
4. Update `.env` file

**Note:** Document upload won't work without S3, but other features work

---

## 📋 Current Status Checklist

Run this to check everything:
```powershell
.\check_status.ps1
```

### Manual Check:

1. **Backend Running?**
   - Open: http://localhost:8000/api/health
   - Should return: `{"status":"healthy",...}`

2. **Frontend Running?**
   - Open: http://localhost:5173
   - Should show login page

3. **Database Running?**
   - Try sign up at http://localhost:8000/api/docs
   - If you get "Database connection failed" → PostgreSQL not running

---

## 🎯 What to Do Right Now

### If Sign Up/Login Not Working:

1. **Check if PostgreSQL is running:**
   ```powershell
   .\start_database.ps1
   ```

2. **Wait 5-10 seconds for database to start**

3. **Try sign up again:**
   - Go to: http://localhost:8000/api/docs
   - Use `/api/v1/auth/register` endpoint
   - Or use frontend: http://localhost:5173

### If Backend Not Running:

1. **Check PowerShell window** - should show "Uvicorn running"
2. **If not, restart:**
   ```powershell
   .\restart_backend.ps1
   ```

### If Frontend Not Running:

1. **Start it:**
   ```powershell
   cd frontend
   npm run dev
   ```

---

## 🔧 Troubleshooting

### "Database connection failed"
**Solution:** Start PostgreSQL
```powershell
.\start_database.ps1
```

### "Backend not responding"
**Solution:** Check backend PowerShell window for errors, restart if needed

### "CORS error"
**Solution:** Make sure backend is running and CORS_ORIGINS in `.env` includes frontend URL

### "Module not found" errors
**Solution:** Install missing dependencies
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📝 Quick Reference

| Service | Port | Required? | Start Command |
|---------|------|-----------|---------------|
| Backend | 8000 | ✅ Yes | `.\restart_backend.ps1` |
| Frontend | 5173 | ✅ Yes | `cd frontend && npm run dev` |
| PostgreSQL | 5432 | ✅ Yes | `.\start_database.ps1` |
| Redis | 6379 | ⚠️ Optional | `docker compose up -d redis` |

---

## 🎉 After Everything is Running

1. **Open Frontend:** http://localhost:5173
2. **Click "Sign up"**
3. **Create your account**
4. **Login and explore!**

---

## 📚 More Help

- **Full Checklist:** See `CHECKLIST.md`
- **Testing Guide:** See `TESTING.md`
- **API Documentation:** http://localhost:8000/api/docs
