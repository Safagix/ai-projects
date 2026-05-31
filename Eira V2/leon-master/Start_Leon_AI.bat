@echo off
title Leon AI Server
echo --- STARTING LEON AI (NODE.JS) ---
echo Directory: %~dp0
cd /d "%~dp0"

echo.
echo [CHECKING NODE.JS]
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado o no esta en el PATH.
    echo Por favor instala Node.js LTS de https://nodejs.org/
    pause
    exit
) else (
    node -v
)

echo.
if not exist "node_modules" (
    echo [WARNING] 'node_modules' folder not found!
    echo It looks like dependencies are not installed.
    echo.
    echo Launching Setup...
    call Setup_Leon.bat
)

echo [STARTING SERVER]
npm start

pause
