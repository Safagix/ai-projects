@echo off
setlocal
title Leon AI Server (ADMIN)

:: ----------------------------------------------------------------
:: ADMIN PRIVILEGE CHECK
:: ----------------------------------------------------------------
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Admin Privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

:: ----------------------------------------------------------------
:: MAIN LOGIC
:: ----------------------------------------------------------------
echo --- STARTING LEON AI ---
echo Directory: %~dp0

echo.
echo [CHECKING NODE.JS]
node -v
if %errorlevel% neq 0 (
    echo [ERROR] Node.js missing!
    goto error
)

echo.
echo [STARTING SERVER]
echo If this crashes instantly, run 'Build_Leon.bat' first!
echo.
call npm start

:: End of script
echo.
echo [SERVER STOPPED]
pause
exit /b

:error
echo.
echo [CRITICAL ERROR]
pause
exit /b
