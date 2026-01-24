# Restart Frontend Server
Write-Host "Restarting Frontend Server..." -ForegroundColor Cyan

# Kill existing Node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

cd frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "`nFrontend: http://localhost:5173`n" -ForegroundColor Green
npm run dev
