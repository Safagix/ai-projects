@echo off
set "NODE_PATH=%DIGITAL_LAB%\nodejs_temp\node-v20.18.0-win-x64"
set "PATH=%NODE_PATH%;%PATH%"
"%NODE_PATH%\node.exe" %*
