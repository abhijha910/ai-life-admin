# AI Life Admin Assistant - Setup Checklist

## Current Status Check

Run this to check your current setup:
```powershell
.\check_status.ps1
```

## Complete Setup Checklist

### ✅ 1. Backend Server
- [ ] Backend is running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/api/docs
- [ ] Health check works: http://localhost:8000/api/health

**To start backend:**
```powershell
.\restart_backend.ps1
# OR
.\start_all.ps1
```

### ✅ 2. Database (PostgreSQL) - REQUIRED for Sign Up/Login
- [ ] PostgreSQL is running
- [ ] Database connection works
- [ ] Tables are created

**To start database:**
```powershell
.\start_database.ps1
# OR manually:
docker compose up -d postgres
```

**To verify database:**
- Try signing up at http://localhost:8000/api/docs
- If you get "Database connection failed" error, PostgreSQL is not running

### ✅ 3. Frontend Server
- [ ] Frontend is running on http://localhost:5173
- [ ] Can access login page

**To start frontend:**
```powershell
cd frontend
npm install  # First time only
npm run dev
```

**Or use:**
```powershell
.\start_all.ps1  # Starts both backend and frontend
```

### ✅ 4. Redis (Optional - for rate limiting and caching)
- [ ] Redis is running (optional for basic functionality)

**To start Redis:**
```powershell
docker compose up -d redis
```

### ✅ 5. AI Features (Optional)
- [ ] Ollama is installed and running
- [ ] Model downloaded: `ollama pull llama3:8b`
- [ ] spaCy model: `python -m spacy download en_core_web_sm`

**To setup AI:**
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3:8b

# Install spaCy model
cd backend
.\venv\Scripts\Activate.ps1
python -m spacy download en_core_web_sm
```

### ✅ 6. AWS S3 (Optional - for document storage)
- [ ] AWS credentials configured in `.env`
- [ ] S3 bucket created

**For local testing without S3:**
- Document upload will fail, but other features work
- You can modify code to use local storage for testing

## Quick Start Commands

### Start Everything (Backend + Frontend)
```powershell
.\start_all.ps1
```

### Start Database Only
```powershell
.\start_database.ps1
```

### Start Backend Only
```powershell
.\restart_backend.ps1
```

### Check Status
```powershell
.\check_status.ps1
```

## Testing the Application

### 1. Test Backend API
1. Open http://localhost:8000/api/docs
2. Test `/api/health` endpoint
3. Try `/api/v1/auth/register` to create a user
4. Try `/api/v1/auth/login` to login

### 2. Test Frontend
1. Open http://localhost:5173
2. Click "Sign up" to create account
3. Login with your credentials
4. Explore the dashboard

### 3. Common Issues

**"Database connection failed"**
- Solution: Start PostgreSQL with `.\start_database.ps1`

**"Backend not responding"**
- Solution: Check if backend PowerShell window is open and running
- Restart with `.\restart_backend.ps1`

**"Frontend not loading"**
- Solution: Check if frontend is running on port 5173
- Start with `cd frontend && npm run dev`

**"CORS error"**
- Solution: Make sure backend is running and CORS_ORIGINS is set correctly

## Required vs Optional

### Required for Basic Functionality:
- ✅ Backend server
- ✅ PostgreSQL database (for user accounts)
- ✅ Frontend server (to use the UI)

### Optional but Recommended:
- Redis (for better performance)
- Ollama (for AI features)
- spaCy model (for NLP)
- AWS S3 (for document storage)

## Next Steps After Setup

1. **Create your first account**
   - Go to http://localhost:5173
   - Click "Sign up"
   - Fill in email, password, name

2. **Explore features**
   - Dashboard with daily plan
   - Email inbox (connect email accounts)
   - Document upload
   - Task management

3. **Connect email accounts**
   - Go to Settings
   - Add Gmail/Outlook/IMAP accounts
   - Sync emails

4. **Upload documents**
   - Go to Documents page
   - Upload PDFs, images
   - AI will extract text and classify

## Troubleshooting

See `TESTING.md` for detailed troubleshooting guide.
