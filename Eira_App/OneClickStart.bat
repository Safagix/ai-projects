@echo off
cd /d "%~dp0"

cls
echo ========================================
echo   EIRA AI // NEURAL LINK LAUNCHER
echo ========================================
echo.
echo Path: %~dp0
echo.

:: [FIX] Use local portable Node.js (Full Runtime with NPM)
set "PATH=%~dp0bin\node-v22.12.0-win-x64;%PATH%"

:: Verify Node
echo Checking Node.js...
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js not found.
    echo We tried to download a portable version but it failed.
    echo Please install it manually from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo   Node.js: %%v
for /f "tokens=*" %%v in ('npm --version') do echo   npm:     %%v (Using system npm)
echo.

:: Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    call npm install
    echo.
)

echo Starting Eira Development Environment...
echo.
call npm run tauri dev

echo.
echo Press any key to exit...
pause > nul
