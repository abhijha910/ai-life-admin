# Setup and Run Script for AI Life Admin Assistant

Write-Host "=== AI Life Admin Assistant - Setup & Run ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
$envPath = "backend\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# Application
APP_NAME=AI Life Admin Assistant
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ailifeadmin
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/ailifeadmin

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# AWS S3 (Optional for local dev)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
S3_PRESIGNED_URL_EXPIRATION=3600

# Email OAuth (Optional for local dev)
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/emails/oauth/callback

OUTLOOK_CLIENT_ID=
OUTLOOK_CLIENT_SECRET=
OUTLOOK_REDIRECT_URI=http://localhost:8000/api/v1/emails/oauth/callback

# AI Engine
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Frontend
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-for-tokens
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"@ | Out-File -FilePath $envPath -Encoding UTF8
    Write-Host ".env file created!" -ForegroundColor Green
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
Write-Host "`nSetting up Python environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    cd backend
    python -m venv venv
    cd ..
    Write-Host "Virtual environment created!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate venv and install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
cd backend
& .\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
Write-Host "Dependencies installed!" -ForegroundColor Green
cd ..

# Check if PostgreSQL and Redis are running (for Docker)
Write-Host "`nChecking for Docker..." -ForegroundColor Yellow
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($dockerVersion) {
        Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
        $dockerAvailable = $true
    }
} catch {
    Write-Host "Docker not found. Will run without Docker." -ForegroundColor Yellow
}

if ($dockerAvailable) {
    Write-Host "`nStarting services with Docker Compose..." -ForegroundColor Yellow
    Write-Host "Note: Make sure PostgreSQL and Redis are accessible" -ForegroundColor Yellow
    Write-Host "`nTo start services, run:" -ForegroundColor Cyan
    Write-Host "  docker compose up -d" -ForegroundColor White
    Write-Host "`nOr start backend manually:" -ForegroundColor Cyan
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
} else {
    Write-Host "`nTo start the backend server:" -ForegroundColor Cyan
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host "`nNote: Make sure PostgreSQL and Redis are running locally" -ForegroundColor Yellow
}

Write-Host "`nTo start the frontend:" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm install" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
