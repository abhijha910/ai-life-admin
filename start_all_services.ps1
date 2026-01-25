# Start All Services Script
Write-Host "`n=== Starting AI Life Admin Services ===`n" -ForegroundColor Cyan

# Step 1: Check Docker
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "  Attempting to start Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "  Waiting 20 seconds for Docker to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
    
    $dockerCheck = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Docker Desktop failed to start!" -ForegroundColor Red
        Write-Host "  Please start Docker Desktop manually and try again.`n" -ForegroundColor Yellow
        Write-Host "  Troubleshooting:" -ForegroundColor Cyan
        Write-Host "  1. Check if WSL 2 is enabled: wsl --status" -ForegroundColor White
        Write-Host "  2. Restart your computer" -ForegroundColor White
        Write-Host "  3. Check Docker Desktop logs" -ForegroundColor White
        exit 1
    }
}
Write-Host "  Docker is running!" -ForegroundColor Green

# Step 2: Start Database
Write-Host "`nStep 2: Starting Database (PostgreSQL + Redis)..." -ForegroundColor Yellow
docker compose up -d postgres redis

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Database containers started!" -ForegroundColor Green
    Write-Host "  Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check database
    $dbCheck = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($dbCheck) {
        Write-Host "  Database is ready on port 5432!" -ForegroundColor Green
    } else {
        Write-Host "  Database is starting... (may take a few more seconds)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: Failed to start database!" -ForegroundColor Red
    exit 1
}

# Step 3: Check Backend Setup
Write-Host "`nStep 3: Checking Backend..." -ForegroundColor Yellow
if (-not (Test-Path ".\backend\venv")) {
    Write-Host "  ERROR: Backend virtual environment not found!" -ForegroundColor Red
    Write-Host "  Please create it first: cd backend; python -m venv venv" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Backend setup OK!" -ForegroundColor Green

# Step 4: Check Frontend Setup
Write-Host "`nStep 4: Checking Frontend..." -ForegroundColor Yellow
if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
}
Write-Host "  Frontend setup OK!" -ForegroundColor Green

# Step 5: Start Backend (in new window)
Write-Host "`nStep 5: Starting Backend..." -ForegroundColor Yellow
Write-Host "  Opening backend in new PowerShell window..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; Write-Host 'Backend starting on http://localhost:8000' -ForegroundColor Green; uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 3

# Step 6: Start Frontend (in new window)
Write-Host "`nStep 6: Starting Frontend..." -ForegroundColor Yellow
Write-Host "  Opening frontend in new PowerShell window..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Frontend starting on http://localhost:5173' -ForegroundColor Green; npm run dev"

# Summary
Write-Host "`n=== Services Starting ===`n" -ForegroundColor Green
Write-Host "Database:  PostgreSQL on port 5432" -ForegroundColor White
Write-Host "Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "API Docs:  http://localhost:8000/api/docs`n" -ForegroundColor White

Write-Host "Check the new PowerShell windows for service logs." -ForegroundColor Cyan
Write-Host "Press Ctrl+C in those windows to stop services.`n" -ForegroundColor Yellow
