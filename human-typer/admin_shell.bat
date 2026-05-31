@echo off
setlocal
cd /d "%~dp0"

:: Comprobar si se tienen permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo [INFO] Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:admin
color 0A
echo ========================================================
echo               Human Typer - Modo Administrador
echo ========================================================
echo.
echo Privilegios de administrador CONCEDIDOS.
echo El modulo "keyboard" y "pyautogui" requieren estos permisos
echo en Windows para capturar pulsaciones y simular eventos.
echo.
echo Directorio actual: %CD%
echo.
echo Puedes usar la herramienta mediante uv o hatch:
echo.
echo   uv run human-typer --help
echo   uv run human-typer train --profile mi_perfil
echo   uv run human-typer type-text "Texto a escribir" --profile mi_perfil
echo.
echo Si estas usando otro gestor como venv o pip:
echo   python -m human_typer --help
echo.
echo ========================================================
cmd /k
