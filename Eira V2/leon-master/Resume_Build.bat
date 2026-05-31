@echo off
title Leon Build RESUME
echo ---------------------------------------------------
echo      LEON AI - RESUME BUILD (SKIP DOWNLOADS)
echo ---------------------------------------------------
echo Attempting to compile the code without re-downloading...
echo.

call npm run build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. 
    echo Please run 'Build_Leon.bat' for a full repair.
    pause
    exit /b
)

echo.
echo [SUCCESS] Build Complete! 
echo You can now try 'Start_Leon_AI_Admin.bat'.
pause
