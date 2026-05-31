@echo off
:: Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting Admin Privileges for Memory Access...
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

echo ---------------------------------------------------
echo      EIRA TRAINING MODE (MEMORY ACCESS)
echo ---------------------------------------------------
echo Linking to Project Starlight Core...

:: We are in g:\Digital Lab\Eira\Memory
:: We need to go to g:\Digital Lab\ProjectStarlight

cd "..\..\ProjectStarlight"

:: Try generic python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python train_eira.py
    pause
    exit
)

:: Try py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    py -3.12 train_eira.py
    pause
    exit
)

echo NO SE ENCONTRO PYTHON.
pause
