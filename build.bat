@echo off
setlocal
cd /d "%~dp0"
title QuickSend LAN - Build executable

where python >nul 2>nul
if errorlevel 1 (
    echo Python est introuvable. Installez Python 3.10+ avec "Add Python to PATH".
    pause
    exit /b 1
)

python -m pip install pyinstaller
if errorlevel 1 (
    echo Echec de l'installation de PyInstaller.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name QuickSend-LAN --hidden-import frontend.windows.main_window --hidden-import customtkinter main.py
if errorlevel 1 (
    echo Echec de la compilation.
    pause
    exit /b 1
)

echo.
echo Executable genere : %~dp0dist\QuickSend-LAN.exe
pause
endlocal
