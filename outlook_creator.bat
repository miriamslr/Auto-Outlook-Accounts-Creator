@echo off
echo ===================================
echo Building outlook_creator.exe
echo ===================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    echo.
)

echo Building executable...
echo.

REM Build the executable
pyinstaller ^
    --onefile ^
    --name "outlook_creator" ^
    --icon=NONE ^
    --clean ^
    --noconfirm ^
    --add-data "requirements.txt;." ^
    --add-data "outlook_account_creator.py;." ^
    --add-data "proxy_manager.py;." ^
    --add-data "config.py;." ^
    --console ^
    setup_and_run.py

echo.
echo ===================================
echo Build Complete!
echo ===================================
echo.
echo The executable is in the 'dist' folder:
echo   dist\outlook_creator.exe
echo.
echo You can distribute this file to users.
echo They just need to run outlook_creator.exe!
echo.
pause
