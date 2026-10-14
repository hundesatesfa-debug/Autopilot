@echo off
setlocal
cd /d "%~dp0\.."

echo ========================================================
echo   AutoPilot AI - Building Standalone Windows Executable
echo ========================================================

REM Verify PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

REM Build using spec file
echo [INFO] Running PyInstaller with pyinstaller.spec...
pyinstaller --clean pyinstaller.spec

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   Build succeeded!
    echo   Executable located at: dist\AutoPilot-AI.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] PyInstaller build failed with exit code %errorlevel%.
)

endlocal
