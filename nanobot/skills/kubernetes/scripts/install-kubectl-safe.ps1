# install-kubectl-safe.ps1
# Simple and reliable wrapper installer

Write-Host "Installing kubectl-safe wrapper..." -ForegroundColor Cyan

$binDir = "$env:USERPROFILE\bin"

# Create bin directory
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    Write-Host "Created directory: $binDir" -ForegroundColor Green
}

# Create kubectl-safe.bat file
$scriptPath = "D:\WorkHome\git\github\nanobot\nanobot\skills\kubernetes\scripts\kubectl-safe.ps1"
$batchContent = @"
@echo off
set "SCRIPT=$scriptPath"
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%SCRIPT%' %*"
"@

$batchPath = "$binDir\kubectl-safe.bat"
$batchContent | Set-Content -Path $batchPath -Encoding ASCII
Write-Host "Created: $batchPath" -ForegroundColor Green

# Add to PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
    Write-Host "Added to PATH. Please restart your terminal." -ForegroundColor Green
} else {
    Write-Host "Directory already in PATH." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[OK] Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Close and reopen your terminal" -ForegroundColor Yellow
Write-Host "2. Test the command: kubectl-safe get pods" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Dangerous commands like 'kubectl-safe delete' will be automatically blocked" -ForegroundColor Gray
