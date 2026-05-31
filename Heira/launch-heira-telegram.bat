@echo off
setlocal
cd /d "%~dp0"
title Heira Telegram Bridge
echo =========================================
echo Iniciando Heira para Telegram...
echo =========================================
call "%~dp0start.cmd"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo.
  echo Heira se cerro con codigo %EXIT_CODE%.
  pause
)
endlocal
