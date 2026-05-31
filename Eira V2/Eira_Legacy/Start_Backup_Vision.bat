@echo off
TITLE Starlight Vision (BACKUP)
CLS
ECHO Lanzando Starlight Vision (Solo Manos, Sin Eira)...
ECHO.
python starlight_vision_backup.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fallo python default. Probando 'py'...
    py starlight_vision_backup.py
)
PAUSE
