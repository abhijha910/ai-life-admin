# Start PostgreSQL Database
Write-Host "Starting PostgreSQL Database..." -ForegroundColor Cyan

# Check if Docker is available
$dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCheck) {
    Write-Host "`nERROR: Docker is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "`nPlease install Docker Desktop:" -ForegroundColor Yellow
    Write-Host "  https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "`nAfter installing, restart your computer and try again.`n" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "`nPlease start Docker Desktop and try again.`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker is running. Starting PostgreSQL..." -ForegroundColor Green

# Start PostgreSQL using docker compose
docker compose up -d postgres

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] PostgreSQL is starting!" -ForegroundColor Green
    Write-Host "`nWaiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check if database is accessible
    $dbCheck = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($dbCheck) {
        Write-Host "[SUCCESS] Database is ready!" -ForegroundColor Green
        Write-Host "`nDatabase Details:" -ForegroundColor Cyan
        Write-Host "  Host: localhost" -ForegroundColor White
        Write-Host "  Port: 5432" -ForegroundColor White
        Write-Host "  Database: ailifeadmin" -ForegroundColor White
        Write-Host "  Username: postgres" -ForegroundColor White
        Write-Host "  Password: postgres" -ForegroundColor White
        Write-Host "`nNow restart your backend:" -ForegroundColor Yellow
        Write-Host "  .\restart_backend.ps1`n" -ForegroundColor White
    } else {
        Write-Host "[INFO] Database is starting... (may take 10-20 seconds)" -ForegroundColor Yellow
        Write-Host "Run: .\restart_backend.ps1 in a few seconds`n" -ForegroundColor Cyan
    }
} else {
    Write-Host "`n[ERROR] Failed to start PostgreSQL!" -ForegroundColor Red
    Write-Host "Check Docker Desktop is running and try again.`n" -ForegroundColor Yellow
    exit 1
}
