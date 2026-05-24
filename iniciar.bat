@echo off
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

echo Carregando modelo de IA (aguarde ~10 segundos)...
echo.
start "" "http://localhost:5000"
timeout /t 6 >nul
venv\Scripts\python app.py
pause
