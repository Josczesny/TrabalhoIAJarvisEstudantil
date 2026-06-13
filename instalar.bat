@echo off
chcp 65001 >nul
echo ================================================
echo  JARVIS Academico - Instalacao
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo Passo 1/4: Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO ao criar ambiente virtual.
    pause
    exit /b 1
)

echo Passo 2/4: Atualizando pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo Passo 3/4: Instalando PyTorch...
venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir --quiet
if errorlevel 1 (
    echo ERRO ao instalar PyTorch.
    pause
    exit /b 1
)

echo Passo 4/4: Instalando demais dependencias...
venv\Scripts\pip install flask openai sentence-transformers faiss-cpu numpy pypdf werkzeug --no-cache-dir --quiet
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