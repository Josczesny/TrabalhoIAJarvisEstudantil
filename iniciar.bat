@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ================================================
echo  JARVIS Academico - Iniciando...
echo ================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Execute primeiro o arquivo: instalar.bat
    pause
    exit /b 1
)

echo Carregando modelo de IA...
echo.

:: Barra de progresso com 20 blocos (~10 segundos)
set "barra="
set /a total=20
set /a delay=500

for /l %%i in (1,1,%total%) do (
    set /a pct=%%i*100/%total%
    set "barra=!barra!█"
    cls
    echo ================================================
    echo  JARVIS Academico - Iniciando...
    echo ================================================
    echo.
    echo  Carregando modelo de IA...
    echo.
    echo  [!barra!] !pct!%%
    echo.
    ping -n 1 -w %delay% 127.0.0.1 >nul
)

cls
echo ================================================
echo  JARVIS Academico - Pronto!
echo ================================================
echo.
echo  Abrindo http://localhost:5000 ...
echo.

start "" "http://localhost:5000"
venv\Scripts\python app.py
pause
