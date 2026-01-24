# Push to GitHub Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Push to GitHub" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$repoName = Read-Host "Enter your GitHub repository name (e.g., 'ai-life-admin')"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    Write-Host "Repository name is required!" -ForegroundColor Red
    exit 1
}

Write-Host "`nSetting up remote..." -ForegroundColor Yellow

# Remove existing remote if any
git remote remove origin 2>$null

# Add new remote
git remote add origin "https://github.com/abhijha910/$repoName.git"

Write-Host "Remote added: https://github.com/abhijha910/$repoName.git" -ForegroundColor Green

Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for GitHub credentials.`n" -ForegroundColor Yellow

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    Write-Host "Repository URL:" -ForegroundColor Cyan
    Write-Host "https://github.com/abhijha910/$repoName" -ForegroundColor White
} else {
    Write-Host "`nPush failed. Common issues:" -ForegroundColor Red
    Write-Host "1. Repository doesn't exist on GitHub - Create it first at https://github.com/new" -ForegroundColor Yellow
    Write-Host "2. Authentication required - Use GitHub Personal Access Token" -ForegroundColor Yellow
    Write-Host "3. Check your internet connection" -ForegroundColor Yellow
}
