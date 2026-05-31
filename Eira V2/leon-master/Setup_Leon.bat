@echo off
title Leon AI Setup (npm install)
echo --- INSTALLING LEON AI DEPENDENCIES ---
echo This may take a few minutes. Please wait...
echo.

cd /d "%~dp0"

echo [EXECUTING] npm install
call npm install

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed.
    echo Please check your internet connection and try again.
    pause
    exit /b
)

echo.
echo [SUCCESS] Dependencies installed!
echo You can now run 'Start_Leon_AI.bat'.
pause
