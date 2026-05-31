@echo off
title EIRA CHAT - ALEXANDRIA EDITION
echo Initializing Eira Chat System...
echo ---------------------------------
echo Loading Alexandria Library Context...
echo Loading Edge-TTS...
echo Loading PyQt6 UI...
echo.

cd /d "%~dp0"
python eira_chat_ui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ SYSTEM ERROR: Eira crashed or closed unexpectedly.
    pause
)
