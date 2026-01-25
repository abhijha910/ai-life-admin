# 🐳 Docker Installation - Next Steps

## Step 1: Wait for Installation to Complete

The Docker Desktop installation window will show:
- ✅ All components installed
- ✅ "Installation complete" message
- ✅ "Launch Docker Desktop" button

**Click "Launch Docker Desktop"** when installation finishes.

## Step 2: Restart Your Computer (If Prompted)

If Docker asks you to restart:
1. **Save all your work**
2. **Click "Restart Now"**
3. **Wait for computer to restart**
4. **Docker Desktop will start automatically**

## Step 3: Start Docker Desktop

After restart (or if no restart needed):

1. **Open Docker Desktop** from:
   - Start Menu → Docker Desktop
   - Desktop shortcut (if created)
   - Search "Docker Desktop"

2. **Wait for Docker to start:**
   - You'll see a whale icon in system tray
   - Docker Desktop window will open
   - Status should say "Docker Desktop is running"

## Step 4: Verify Docker is Working

Open PowerShell and run:

```powershell
# Check Docker version
docker --version

# Check if Docker is running
docker ps

# Check Docker info
docker info
```

**Expected output:**
- `docker --version` should show: `Docker version 24.x.x` or similar
- `docker ps` should show: Empty list (no containers running yet) - this is OK!
- `docker info` should show Docker system information

## Step 5: Start Your Database

Once Docker is running, start PostgreSQL:

```powershell
cd "C:\Users\abh jha\OneDrive\All_Apps_Websites\ai-life-admin"
.\start_database.ps1
```

This will:
- Download PostgreSQL image (first time only)
- Start PostgreSQL container
- Start Redis container
- Wait for database to be ready

## Step 6: Verify Database is Running

```powershell
# Check running containers
docker ps

# You should see:
# - postgres container running
# - redis container (if using)
```

## Step 7: Start Your Backend

After database is running:

```powershell
.\start_backend.ps1
```

The backend will:
- Connect to PostgreSQL
- Create database tables
- Start API server on http://localhost:8000

## Step 8: Start Your Frontend

In a new PowerShell window:

```powershell
cd "C:\Users\abh jha\OneDrive\All_Apps_Websites\ai-life-admin"
.\start_frontend.ps1
```

Frontend will start on http://localhost:5173

## Troubleshooting

### Docker Desktop won't start?
- Make sure virtualization is enabled in BIOS
- Check Windows features: WSL 2 should be enabled
- Restart computer

### "Docker is not running" error?
- Open Docker Desktop manually
- Wait for it to fully start (whale icon in system tray)
- Check system tray for Docker icon

### Port already in use?
```powershell
# Check what's using port 5432 (PostgreSQL)
netstat -ano | findstr :5432

# Stop Docker containers
docker compose down
```

## Quick Commands Reference

```powershell
# Start database
.\start_database.ps1

# Start backend
.\start_backend.ps1

# Start frontend
.\start_frontend.ps1

# Check Docker containers
docker ps

# Stop all containers
docker compose down

# View container logs
docker compose logs postgres
```

## What's Next?

Once everything is running:
- ✅ Database: PostgreSQL on port 5432
- ✅ Backend: FastAPI on http://localhost:8000
- ✅ Frontend: React on http://localhost:5173
- ✅ Sign up/Login should work!

---

**After Docker installation completes, follow these steps in order!**
