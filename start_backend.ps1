# Start Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
cd backend

if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    exit 1
}

.\venv\Scripts\Activate.ps1
Write-Host "`nBackend: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/api/docs`n" -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8000
