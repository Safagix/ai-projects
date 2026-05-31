@echo off
set "SOURCE=g:\Digital Lab\ProjectStarlight"
set "MEM_SOURCE=g:\Digital Lab\Eira\Memory"
set "DEST=g:\Digital Lab\Backups\Starlight_Stable_v2.5"

echo CREATING BACKUP AT: %DEST%
if not exist "%DEST%" mkdir "%DEST%"

echo Copying Core Systems...
copy "%SOURCE%\main_eira_lab.py" "%DEST%"
copy "%SOURCE%\eira_brain.py" "%DEST%"
copy "%SOURCE%\eira_skills.py" "%DEST%"
copy "%SOURCE%\hand_controller.py" "%DEST%"
copy "%SOURCE%\holographic_ui.py" "%DEST%"
copy "%SOURCE%\train_eira.py" "%DEST%"

echo Copying Utilities & Launchers...
copy "%SOURCE%\Start_Eira_Lab_Admin.bat" "%DEST%"
copy "%SOURCE%\Kill_All_Eira.bat" "%DEST%"
copy "%SOURCE%\starlight_vision_backup.py" "%DEST%"
copy "%SOURCE%\requirements.txt" "%DEST%"

echo Copying Memory Tools...
copy "%MEM_SOURCE%\Start_Eira_Chat_Admin.bat" "%DEST%"

echo.
echo ---------------------------------------
echo ✅ BACKUP COMPLETE.
echo Files saved to: %DEST%
echo ---------------------------------------
pause
