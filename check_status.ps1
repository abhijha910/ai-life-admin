# Check Status of All Services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Life Admin - Status Check" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Backend
Write-Host "1. Backend Server (port 8000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3
    Write-Host "   ✓ RUNNING" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
    $health = $response.Content | ConvertFrom-Json
    Write-Host "   Environment: $($health.environment)" -ForegroundColor White
} catch {
    Write-Host "   ✗ NOT RUNNING" -ForegroundColor Red
    Write-Host "   Start with: .\restart_backend.ps1" -ForegroundColor Yellow
}

# Check Frontend
Write-Host "`n2. Frontend Server (port 5173):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 3
    Write-Host "   ✓ RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   ✗ NOT RUNNING" -ForegroundColor Yellow
    Write-Host "   Start with: cd frontend && npm run dev" -ForegroundColor Yellow
}

# Check PostgreSQL
Write-Host "`n3. PostgreSQL Database:" -ForegroundColor Yellow
$postgresRunning = $false
try {
    $containers = docker ps --filter "name=postgres" --format "{{.Names}}" 2>&1
    if ($containers -and $containers -notmatch "error") {
        Write-Host "   ✓ RUNNING (Docker)" -ForegroundColor Green
        Write-Host "   Container: $containers" -ForegroundColor White
        $postgresRunning = $true
    } else {
        # Try to connect to check if local PostgreSQL is running
        try {
            $testConn = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue
            if ($testConn.TcpTestSucceeded) {
                Write-Host "   ✓ RUNNING (Local)" -ForegroundColor Green
                $postgresRunning = $true
            } else {
                Write-Host "   ✗ NOT RUNNING" -ForegroundColor Red
                Write-Host "   Start with: .\start_database.ps1" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ✗ NOT RUNNING" -ForegroundColor Red
            Write-Host "   Start with: .\start_database.ps1" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ✗ NOT RUNNING" -ForegroundColor Red
    Write-Host "   Start with: .\start_database.ps1" -ForegroundColor Yellow
}

# Check Redis
Write-Host "`n4. Redis Cache:" -ForegroundColor Yellow
try {
    $containers = docker ps --filter "name=redis" --format "{{.Names}}" 2>&1
    if ($containers -and $containers -notmatch "error") {
        Write-Host "   ✓ RUNNING (Docker)" -ForegroundColor Green
    } else {
        try {
            $testConn = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
            if ($testConn.TcpTestSucceeded) {
                Write-Host "   ✓ RUNNING (Local)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠ NOT RUNNING (Optional)" -ForegroundColor Yellow
                Write-Host "   Start with: docker compose up -d redis" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠ NOT RUNNING (Optional)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ⚠ NOT RUNNING (Optional)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($postgresRunning) {
    Write-Host "✓ Database is ready - Sign up/Login should work!" -ForegroundColor Green
} else {
    Write-Host "✗ Database NOT running - Sign up/Login will fail" -ForegroundColor Red
    Write-Host "  Run: .\start_database.ps1" -ForegroundColor Yellow
}

Write-Host "`nAccess Points:" -ForegroundColor Cyan
Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8000/api/docs" -ForegroundColor White

Write-Host ""
Write-Host "For complete setup guide, see: CHECKLIST.md" -ForegroundColor Yellow
Write-Host ""
