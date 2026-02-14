# UPI Mule Account Detection - PowerShell Starter
# Run from project root: .\start-all.ps1

Write-Host ""
Write-Host "========================================"
Write-Host "  UPI Mule Detection System - Starter" -ForegroundColor Cyan
Write-Host "========================================" 
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "ERROR: Please run this from the project root directory!" -ForegroundColor Red
    Write-Host "Expected: C:\Users\suvom\OneDrive\Desktop\ICRH\FinalS\UPI_Mule_Account_Detection\" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting Backend (FastAPI) on port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app:app --port 8001 --reload" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "Starting Frontend (React) on port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================"
Write-Host "  Services Starting..." -ForegroundColor Cyan
Write-Host "========================================" 
Write-Host ""
Write-Host "Backend:  http://localhost:8001" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host ""
Write-Host "Open your browser to: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop: Close the terminal windows" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue"
