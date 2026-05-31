@echo off
title Eira AVA - Digital Life Form

REM Admin Check
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [ADMIN] Privileges Confirmed.
) else (
    echo [REQ] Requesting Admin Privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo Initializing Eira AVA System...
echo [BRAIN] Connecting to local Ollama (gemma2:2b)...
echo [BODY] Preparing 60FPS Asset Engine...
cd /d "%DIGITAL_LAB%\Eira_Chat"
python eira_chat_ui.py
pause
