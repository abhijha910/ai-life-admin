# Start Both Backend and Frontend Servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting AI Life Admin Assistant" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}
Write-Host "Found: $nodeVersion" -ForegroundColor Green

# Install frontend dependencies if needed
cd frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "Frontend dependencies installed!`n" -ForegroundColor Green
} else {
    Write-Host "Frontend dependencies already installed`n" -ForegroundColor Green
}
cd ..

# Start Backend in new window
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
$backendScript = @"
cd '$PWD\backend'
.\venv\Scripts\Activate.ps1
Write-Host 'Backend starting on http://localhost:8000' -ForegroundColor Green
Write-Host 'API Docs: http://localhost:8000/api/docs' -ForegroundColor Cyan
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
$frontendScript = @"
cd '$PWD\frontend'
Write-Host 'Frontend starting on http://localhost:5173' -ForegroundColor Green
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Servers Starting!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs`n" -ForegroundColor Cyan
Write-Host "Two new PowerShell windows have opened:" -ForegroundColor Yellow
Write-Host "  • One for Backend (port 8000)" -ForegroundColor White
Write-Host "  • One for Frontend (port 5173)" -ForegroundColor White
Write-Host "`nClose those windows to stop the servers.`n" -ForegroundColor Yellow
