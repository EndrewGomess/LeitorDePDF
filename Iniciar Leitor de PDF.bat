@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo Ambiente virtual nao encontrado: .venv
    echo Instale as dependencias conforme o README.md e tente novamente.
    pause
    exit /b 1
)

start "Leitor de PDF D&D" "%PYTHON%" -m streamlit run "%~dp0app.py" --server.address 127.0.0.1
