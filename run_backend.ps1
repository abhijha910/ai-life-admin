# Quick Start Backend Server
Write-Host "Starting AI Life Admin Backend..." -ForegroundColor Cyan
cd backend
.\venv\Scripts\Activate.ps1
Write-Host "`nBackend server starting on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
