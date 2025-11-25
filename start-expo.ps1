Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SmartSort AI - Starting Expo Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "$PSScriptRoot\mobile"

Write-Host "Current directory: $PWD" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Expo development server..." -ForegroundColor Yellow
Write-Host "QR Code will appear below!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

npx expo start

