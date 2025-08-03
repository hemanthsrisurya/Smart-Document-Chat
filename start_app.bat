@echo off
:: Smart Document Chat - Simple Windows Launcher
:: Double-click this file to start the application

title Smart Document Chat

echo.
echo ========================================
echo  Smart Document Chat - Quick Launcher
echo ========================================
echo.

:: Check if we're in the right directory
if not exist "app.py" (
    echo ERROR: Please place this file in the same folder as app.py
    echo.
    pause
    exit /b 1
)

:: Try to run the PowerShell script first
echo Attempting to start Smart Document Chat...
echo.

powershell -ExecutionPolicy Bypass -File "run_app.ps1"

:: If that fails, show instructions
if errorlevel 1 (
    echo.
    echo ========================================
    echo  Manual Setup Required
    echo ========================================
    echo.
    echo It looks like the automatic setup failed.
    echo Please run the installer first:
    echo.
    echo 1. Right-click on "install.ps1"
    echo 2. Select "Run with PowerShell"
    echo 3. Wait for installation to complete
    echo 4. Then run this launcher again
    echo.
    echo Alternatively, you can install manually:
    echo 1. Install Python from https://python.org
    echo 2. Install Ollama from https://ollama.ai
    echo 3. Open Command Prompt in this folder
    echo 4. Run: pip install -r requirements.txt
    echo 5. Run: ollama serve
    echo 6. Run: ollama pull gemma3:4b
    echo 7. Run: streamlit run app.py
    echo.
)

pause
