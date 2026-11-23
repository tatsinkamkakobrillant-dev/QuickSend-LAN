@echo off
setlocal
cd /d "%~dp0"
title QuickSend LAN

where python >nul 2>nul
if errorlevel 1 (
    echo Python est introuvable.
    echo Installez Python 3.10 ou plus recent depuis https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" pendant l'installation.
    pause
    exit /b 1
)

python -c "import customtkinter" >nul 2>nul
if errorlevel 1 (
    echo Installation des dependances...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Echec de l'installation des dependances.
        pause
        exit /b 1
    )
)

echo Lancement de QuickSend LAN...
python main.py %*
if errorlevel 1 pause
endlocal
