# Restart Backend Server
Write-Host "Restarting Backend Server..." -ForegroundColor Cyan
cd backend
.\venv\Scripts\Activate.ps1
Write-Host "`nBackend server starting on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/api/docs`n" -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
