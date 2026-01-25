# Comprehensive Status Check Script
Write-Host "`n=== AI Life Admin - System Status Check ===`n" -ForegroundColor Cyan

# Check Docker
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Docker installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Docker not found!" -ForegroundColor Red
    exit 1
}

# Check if Docker Desktop is running
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Docker Desktop is running" -ForegroundColor Green
} else {
    Write-Host "   ✗ Docker Desktop is NOT running!" -ForegroundColor Red
    Write-Host "   → Please start Docker Desktop manually" -ForegroundColor Yellow
    Write-Host "   → Or run: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'" -ForegroundColor Yellow
}

Write-Host "`n2. Checking Docker Containers..." -ForegroundColor Yellow
$containers = docker ps -a 2>&1
if ($LASTEXITCODE -eq 0) {
    if ($containers -match "CONTAINER") {
        Write-Host "   Containers found:" -ForegroundColor Green
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    } else {
        Write-Host "   No containers found" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Cannot check containers (Docker not running)" -ForegroundColor Red
}

Write-Host "`n3. Checking Ports..." -ForegroundColor Yellow
$ports = @(8000, 5173, 5432, 6379)
foreach ($port in $ports) {
    $check = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue 2>$null
    if ($check) {
        $service = switch ($port) {
            8000 { "Backend API" }
            5173 { "Frontend" }
            5432 { "PostgreSQL" }
            6379 { "Redis" }
        }
        Write-Host "   ✓ Port $port is in use ($service)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Port $port is free" -ForegroundColor Gray
    }
}

Write-Host "`n4. Checking Backend..." -ForegroundColor Yellow
$backendPath = ".\backend"
if (Test-Path $backendPath) {
    Write-Host "   ✓ Backend directory exists" -ForegroundColor Green
    
    if (Test-Path "$backendPath\venv") {
        Write-Host "   ✓ Virtual environment exists" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Virtual environment not found" -ForegroundColor Red
    }
    
    if (Test-Path "$backendPath\.env") {
        Write-Host "   ✓ .env file exists" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ .env file not found (using defaults)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Backend directory not found" -ForegroundColor Red
}

Write-Host "`n5. Checking Frontend..." -ForegroundColor Yellow
$frontendPath = ".\frontend"
if (Test-Path $frontendPath) {
    Write-Host "   ✓ Frontend directory exists" -ForegroundColor Green
    
    if (Test-Path "$frontendPath\node_modules") {
        Write-Host "   ✓ node_modules exists" -ForegroundColor Green
    } else {
        Write-Host "   ✗ node_modules not found (run: npm install)" -ForegroundColor Red
    }
} else {
    Write-Host "   ✗ Frontend directory not found" -ForegroundColor Red
}

Write-Host "`n=== Status Check Complete ===`n" -ForegroundColor Cyan
