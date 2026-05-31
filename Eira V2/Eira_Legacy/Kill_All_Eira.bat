@echo off
echo MOTHERBOARD OVERRIDE: KILLING ALL PYTHON PROCESSES...
taskkill /IM python.exe /F
taskkill /IM py.exe /F
echo.
echo ------------------------------------------
echo  ALL EIRA SYSTEMS TERMINATED.
echo  GHOST PROCESSES CLEARED.
echo ------------------------------------------
pause
