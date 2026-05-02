@echo off
:: Start Dashboard.bat
:: Double-click this to launch the Upwork Dashboard.
:: It checks for Python, then hands off to the hidden VBS launcher.

title Upwork Dashboard — Starting...

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not on PATH.
    echo.
    echo Please install Python 3.10 or newer from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

:: ── Check Chrome ──────────────────────────────────────────────────────────────
if not exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    if not exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
        echo Google Chrome is not installed.
        echo.
        echo Please install Chrome from https://www.google.com/chrome/
        echo.
        pause
        start https://www.google.com/chrome/
        exit /b 1
    )
)

:: ── Launch silently via VBScript ──────────────────────────────────────────────
wscript "%~dp0run_hidden.vbs"

:: Small message in case they ran the .bat directly
echo Dashboard is starting... your browser will open in a moment.
echo You can close this window.
timeout /t 3 >nul
exit /b 0
