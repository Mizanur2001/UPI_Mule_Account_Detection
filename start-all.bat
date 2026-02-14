@echo off
REM UPI Mule Account Detection - Start All Services
REM This script starts both backend and frontend in separate windows

echo.
echo ========================================
echo   UPI Mule Detection System - Starter
echo ========================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo ERROR: Please run this from the project root directory!
    echo Expected: C:\Users\suvom\OneDrive\Desktop\ICRH\FinalS\UPI_Mule_Account_Detection\
    pause
    exit /b 1
)

echo Starting Backend (FastAPI) on port 8001...
start "UPI Backend" cmd /k "cd backend && python -m uvicorn app:app --port 8001 --reload"

timeout /t 2

echo Starting Frontend (React) on port 3000...
start "UPI Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 2

echo.
echo ========================================
echo   Services Starting...
echo ========================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Open your browser to: http://localhost:3000
echo.
echo To stop, close the terminal windows
echo.
pause
