@echo off
TITLE Instalador de Cerebro Local (Ollama)
CLS
ECHO =================================================
ECHO   INSTALANDO CEREBRO LOCAL PARA EIRA (OLLAMA)
ECHO =================================================
ECHO.
ECHO Para que Eira funcione sin internet y gratis en tu PC,
ECHO necesitamos 'Ollama'.
ECHO.
ECHO 1. Se abrira la pagina web de Ollama.
ECHO 2. Descargalo e Instalalo (Es Siguiente, Siguiente...).
ECHO 3. Cuando termine, abre una terminal y escribe: 
ECHO    ollama run gemma2:2b
ECHO.
ECHO Presiona una tecla para ir a la descarga...
PAUSE
start https://ollama.com/download
ECHO.
ECHO Despues de instalar, vuelve a ejecutar 'Start_Eira_Lab.bat'
PAUSE
