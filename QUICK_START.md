# Quick Start Guide - AI Life Admin

## Current System Status

✅ **Docker**: Installed (v29.1.3)  
✅ **Backend**: Ready (Python venv configured)  
✅ **Frontend**: Ready (node_modules installed)  
❌ **WSL 2**: Not installed (required for Docker Desktop)  
❌ **Database**: Not running (requires Docker)

---

## 🚀 Quick Start (After WSL 2 Installation)

### Step 1: Install WSL 2

**Run PowerShell as Administrator** and execute:
```powershell
wsl --install
```

This will:
- Install WSL 2
- Install Ubuntu (default Linux distribution)
- Configure Docker Desktop to use WSL 2

**After installation, RESTART your computer.**

### Step 2: Start All Services

After restart, open PowerShell in the project directory:
```powershell
cd "C:\Users\abh jha\OneDrive\All_Apps_Websites\ai-life-admin"
.\start_all_services.ps1
```

This script will:
1. ✅ Check Docker Desktop
2. ✅ Start PostgreSQL database
3. ✅ Start Redis
4. ✅ Start Backend API (http://localhost:8000)
5. ✅ Start Frontend (http://localhost:5173)

### Step 3: Verify Services

Open your browser:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

---

## 🔧 Manual Start (If Script Doesn't Work)

### Start Database
```powershell
.\start_database.ps1
```

### Start Backend (in new terminal)
```powershell
.\start_backend.ps1
```

### Start Frontend (in new terminal)
```powershell
.\start_frontend.ps1
```

---

## ⚠️ Alternative: Start Without Docker (Limited)

If you can't install WSL 2 right now, you can start backend/frontend without database:

### Backend (will show database warnings)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm run dev
```

**Note**: Database features (authentication, data storage) won't work without PostgreSQL.

---

## 📋 Service URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:5173 | Ready |
| Backend API | http://localhost:8000 | Ready |
| API Docs | http://localhost:8000/api/docs | Ready |
| PostgreSQL | localhost:5432 | Requires Docker |
| Redis | localhost:6379 | Requires Docker |

---

## 🐛 Troubleshooting

### "Docker Desktop is unable to start"
- **Solution**: Install WSL 2 (see Step 1)
- **Check**: Run `wsl --status` to verify

### "Port already in use"
```powershell
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### "Database connection failed"
- Make sure Docker Desktop is running
- Check containers: `docker ps`
- Restart database: `docker compose restart postgres`

### Backend shows spaCy warning
- This is optional - NLP features may not work
- To fix: `cd backend; .\venv\Scripts\python.exe -m spacy download en_core_web_sm`

---

## 📝 Next Steps After Starting

1. **Create an account**: Go to http://localhost:5173/register
2. **Login**: Use the registration credentials
3. **Explore features**: 
   - Document Scanner
   - Email Inbox
   - Task Management
   - Daily Plans

---

**Need Help?** Check `SYSTEM_STATUS_REPORT.md` for detailed diagnostics.
