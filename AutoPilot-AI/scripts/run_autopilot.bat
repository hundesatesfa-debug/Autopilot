@echo off
setlocal
cd /d "%~dp0\.."

echo ========================================================
echo   AutoPilot AI - Universal Coding Agent Automation
echo ========================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    pause
    exit /b 1
)

REM Set PYTHONPATH and launch AutoPilot AI
set PYTHONPATH=%cd%
python -m autopilot.main %*

if %errorlevel% neq 0 (
    echo.
    echo Application exited with code %errorlevel%.
    pause
)
endlocal
