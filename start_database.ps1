# Start PostgreSQL Database with Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting PostgreSQL Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Docker is available
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($dockerVersion) {
        Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
        $dockerAvailable = $true
    }
} catch {
    Write-Host "Docker not found." -ForegroundColor Yellow
}

if ($dockerAvailable) {
    Write-Host "`nStarting PostgreSQL with Docker..." -ForegroundColor Yellow
    
    # Check if docker-compose.yml exists
    if (Test-Path "docker-compose.yml") {
        docker compose up -d postgres redis
        Write-Host "`nPostgreSQL and Redis starting..." -ForegroundColor Green
        Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        Write-Host "`nDatabase should be ready!" -ForegroundColor Green
        Write-Host "Connection: postgresql://postgres:postgres@localhost:5432/ailifeadmin" -ForegroundColor Cyan
        Write-Host "`nTo check status: docker compose ps" -ForegroundColor Yellow
        Write-Host "To stop: docker compose down`n" -ForegroundColor Yellow
    } else {
        Write-Host "docker-compose.yml not found. Starting PostgreSQL container directly..." -ForegroundColor Yellow
        docker run -d `
            --name ai-life-admin-postgres `
            -e POSTGRES_USER=postgres `
            -e POSTGRES_PASSWORD=postgres `
            -e POSTGRES_DB=ailifeadmin `
            -p 5432:5432 `
            postgres:15-alpine
        
        Write-Host "`nPostgreSQL container started!" -ForegroundColor Green
        Write-Host "Connection: postgresql://postgres:postgres@localhost:5432/ailifeadmin" -ForegroundColor Cyan
        Write-Host "`nTo stop: docker stop ai-life-admin-postgres" -ForegroundColor Yellow
        Write-Host "To remove: docker rm ai-life-admin-postgres`n" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nDocker is not available. Options:" -ForegroundColor Yellow
    Write-Host "1. Install Docker Desktop for Windows" -ForegroundColor White
    Write-Host "2. Install PostgreSQL locally and start it" -ForegroundColor White
    Write-Host "3. Use a cloud PostgreSQL service`n" -ForegroundColor White
    
    Write-Host "For local PostgreSQL installation:" -ForegroundColor Cyan
    Write-Host "  Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  Default connection: postgresql://postgres:postgres@localhost:5432/ailifeadmin`n" -ForegroundColor White
}
