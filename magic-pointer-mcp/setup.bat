@echo off
setlocal EnableExtensions
set "PROJECT_DIR=%~dp0"
title Magic Pointer MCP - Setup
pushd "%PROJECT_DIR%"

echo.
echo ============================================
echo  MAGIC POINTER MCP - Setup
echo ============================================
echo.

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)
echo Python OK.

echo.
echo [2/5] Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
    python -m venv ".venv"
    if errorlevel 1 (
        echo ERROR: Failed to create .venv
        pause
        exit /b 1
    )
)
echo .venv ready.

echo.
echo [3/5] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -e . >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed.

echo.
echo [4/5] Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo Ollama not running. Attempting to start...
    start "" /min ollama serve
    timeout /t 8 /nobreak >nul
    ollama list >nul 2>&1
    if errorlevel 1 (
        echo.
        echo WARNING: Ollama is not responding.
        echo Please install Ollama from https://ollama.com and run: ollama serve
        echo Then run: ollama pull moondream:latest
        echo.
    ) else (
        echo Ollama OK.
    )
) else (
    echo Ollama OK.
)

echo.
echo [5/5] Checking moondream model...
ollama list 2>nul | findstr /i "moondream" >nul
if errorlevel 1 (
    echo.
    echo moondream model not found. Downloading...
    echo This will take a few minutes (~1.9GB)...
    echo.
    ollama pull moondream:latest
    if errorlevel 1 (
        echo WARNING: Failed to pull moondream. Run manually: ollama pull moondream:latest
    ) else (
        echo moondream downloaded.
    )
) else (
    echo moondream OK.
)

echo.
echo ============================================
echo  SETUP COMPLETE
echo ============================================
echo.
echo To run: .venv\Scripts\python.exe server.py
echo Or:     .venv\Scripts\python.exe -m server
echo.
echo Mode: auto (change MAGIC_MODE in .env to "guided")
echo.
pause

popd
