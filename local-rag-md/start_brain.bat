@echo off
setlocal EnableExtensions
title Eira Brain Chat

set "PROJECT_DIR=%~dp0"
set "PY=%PROJECT_DIR%.venv\Scripts\python.exe"
set "HOST=127.0.0.1"
set "PORT=8000"

echo.
echo ============================================
echo  EIRA BRAIN CHAT - Starting
echo ============================================
echo.

pushd "%PROJECT_DIR%" || (
    echo ERROR: No se pudo entrar al proyecto: %PROJECT_DIR%
    pause
    exit /b 1
)

echo [1/7] Verificando Ollama...
set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
set "OLLAMA_MODELS=%DIGITAL_LAB%\ollama-models"
if not exist "%OLLAMA_MODELS%" mkdir "%OLLAMA_MODELS%"
ollama list >nul 2>&1
if errorlevel 1 (
    echo Ollama no responde. Intentando iniciar ollama serve...
    start "Ollama" /min ollama serve
    timeout /t 8 /nobreak >nul
    ollama list >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Ollama sigue sin responder.
        echo Abri Ollama Desktop o ejecuta: ollama serve
        pause
        exit /b 1
    )
)
echo Ollama activo.
echo.
echo [2/7] Verificando OptiLLM...
echo OptiLLM deshabilitado. Usando Ollama directo.
set "OPTILLM_ENABLED_VAR=false"

echo.
echo [3/7] Preparando entorno Python...
if not exist "%PY%" (
    python -m venv ".venv"
    if errorlevel 1 (
        echo ERROR: No se pudo crear .venv.
        pause
        exit /b 1
    )
)
"%PY%" -m pip install -e .
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo [4/7] Validando configuracion y modelos...
"%PY%" -m local_rag.cli doctor
if errorlevel 1 (
    echo.
    echo ERROR: El chequeo inicial fallo. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

echo.
echo [5/7] Inicializando base de datos...
"%PY%" -m local_rag.cli init-db
if errorlevel 1 (
    echo ERROR: No se pudo inicializar la base de datos.
    pause
    exit /b 1
)

echo.
echo [6/7] Verificando indice RAG...
for /f "usebackq delims=" %%A in (`"%PY%" -m local_rag.cli stats --field chunks`) do set "CHUNKS=%%A"
if "%CHUNKS%"=="0" (
    echo La base esta vacia. Creando un indice inicial pequeno para poder probar el chat...
    echo Para indexar todo despues, usa el boton Re-indexar o ejecuta: .venv\Scripts\python.exe -m local_rag.cli ingest
    "%PY%" -m local_rag.cli ingest --max-files 40
    if errorlevel 1 (
        echo ERROR: Fallo la indexacion.
        pause
        exit /b 1
    )
) else (
    echo Indice listo: %CHUNKS% chunks.
)

echo.
echo [7/7] Revisando puerto %PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-NetTCPConnection -LocalAddress '%HOST%' -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }"
if errorlevel 1 (
    echo ERROR: El puerto %PORT% ya esta ocupado.
    echo Cierra el proceso anterior de Eira Brain o cambia el puerto en este .bat.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Eira Brain Chat
echo  http://%HOST%:%PORT%
echo ============================================
echo.

start "" "http://%HOST%:%PORT%"
"%PY%" -m local_rag.cli serve --host %HOST% --port %PORT%

popd
pause
