@echo off
:: Request Admin
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

title Leon AI Builder (ADMIN FORCE)
echo --- BUILDING LEON AI (ADMIN AND UNLOCK) ---
echo.

echo [STEP 0/3] Cleaning up Locks...
echo Killing stuck node.exe processes that might cause EPERM errors...
taskkill /F /IM node.exe >nul 2>&1
echo Done.

echo.
echo [STEP 1/3] Repairing Dependencies...
echo Force cleaning NPM cache...
call npm cache clean --force
echo Deleting old node_modules...
if exist "node_modules" rmdir /s /q "node_modules"
if exist "package-lock.json" del /f /q "package-lock.json"

echo Force installing 'cross-env' and core packages...
call npm install cross-env --save-dev
call npm install

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Dependency install failed.
    echo If this persists, try deleting the 'node_modules' folder manually.
    pause
    exit /b
)

echo.
echo [STEP 2/3] Building Server AND App...
echo Executing 'npm run build'...
call npm run build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed during compilation!
    pause
    exit /b
)

echo.
echo [STEP 3/3] Build Complete!
echo You can now run Start_Leon_AI_Admin.bat
pause
