@echo off
SETLOCAL
:: Ensure we are in the project root
cd /d "%~dp0"

:: Use the virtual environment's python to run the main entry point
if exist ".venv\Scripts\python.exe" (
    echo [MOTHERSHIP] Initializing Local Deck...
    ".venv\Scripts\python.exe" main.py %*
) else (
    echo [ERROR] Virtual environment not found. Please run: python -m venv .venv
    pause
)
ENDLOCAL
