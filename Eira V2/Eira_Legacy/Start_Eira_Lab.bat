@echo off
TITLE Eira Digital Lab - Launcher
CLS
ECHO =================================================
ECHO   INICIANDO EIRA DIGITAL LAB (Project Starlight)
ECHO =================================================
ECHO.
ECHO Detectando entorno correcto...

:: Try to run with the system python (likely 3.12 which works)
python main_eira_lab.py

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Algo fallo. Intentando con 'py' launcher...
    py main_eira_lab.py
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [CRITICAL] No se pudo iniciar. Revisa que Python este instalado.
    PAUSE
)
ECHO.
ECHO Sistema cerrado.
PAUSE
