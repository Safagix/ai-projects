@echo off
TITLE Descargando Cerebro de Eira (Gemma 2)
CLS
ECHO =================================================
ECHO   DESCARGANDO MODELO DE IA (CEREBRO)
ECHO =================================================
ECHO.
ECHO Eira necesita un modelo para pensar. 
ECHO Vamos a descargar 'gemma2:2b' (Google Gemma 2 - 2 Billones de parametros).
ECHO Es ligero y perfecto para tu Ryzen 3.
ECHO.
ECHO Esto puede tardar unos minutos dependiendo de tu internet (1.5 GB aprox).
ECHO.
PAUSE

ollama pull gemma2:2b

ECHO.
ECHO =================================================
ECHO   DESCARGA COMPLETA
ECHO =================================================
ECHO.
ECHO Ahora puedes cerrar esta ventana y abrir 'Start_Eira_Lab.bat'.
PAUSE
