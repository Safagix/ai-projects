@echo off
:: Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: If error flag set, we do not have admin.
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

echo ---------------------------------------------------
echo      EIRA DIGITAL LAB - ADMINISTRATOR MODE
echo ---------------------------------------------------
echo Detectando entorno correcto...

:: Try generic python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Usando 'python' global...
    python main_eira_lab.py
    pause
    exit
)

:: Try py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Usando 'py' launcher (3.12)...
    py -3.12 main_eira_lab.py
    pause
    exit
)

echo NO SE ENCONTRO PYTHON.
pause
