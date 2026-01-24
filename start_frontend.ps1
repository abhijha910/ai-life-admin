# Start Frontend Server
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
cd frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "`nFrontend: http://localhost:5173`n" -ForegroundColor Green
npm run dev
