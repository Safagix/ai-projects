@echo off
title Leon AI Manual Start
echo --- LEON AI MANUAL START ---
echo 1. If this window closes immediately, something is blocking batch files.
echo 2. We are checking Node versions below:
echo.

echo [NODE CHECK]
node -v
if %errorlevel% neq 0 echo Node not found!

echo.
echo [NPM CHECK]
call npm -v
if %errorlevel% neq 0 echo NPM not found!

echo.
echo [INSTALLING DEPENDENCIES]
if not exist "node_modules" (
    echo Installing... (This takes time)
    call npm install
) else (
    echo node_modules exists. Skipping install.
)

echo.
echo [STARTING SERVER]
call npm start

echo.
echo [FINISHED]
pause
