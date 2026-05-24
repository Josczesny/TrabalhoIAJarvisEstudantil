@echo off
chcp 65001 >nul
echo ================================================
echo  JARVIS Academico - Instalacao
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    echo Instale em: https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

echo Passo 1/3: Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO ao criar ambiente virtual.
    pause
    exit /b 1
)

echo Passo 2/3: Instalando PyTorch (pode demorar 5-10 minutos)...
venv\Scripts\pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo ERRO ao instalar PyTorch.
    pause
    exit /b 1
)

echo Passo 3/3: Instalando demais dependencias...
venv\Scripts\pip install flask openai "sentence-transformers==3.3.1" "transformers==4.46.3" faiss-cpu numpy pypdf werkzeug --quiet
if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Instalacao concluida com sucesso!
echo  Agora execute: iniciar.bat
echo ================================================
pause
