@echo off
REM Streamlit GUI Launcher for PDF-to-Narrated-PowerPoint System
REM This script starts the Streamlit web interface

title PDF to PowerPoint Converter - Streamlit GUI
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   PDF-to-Narrated-PowerPoint Converter - Streamlit GUI         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Starting Streamlit application...
echo.

REM Get the directory of this script
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Streamlit is not installed. Installing...
    python -m pip install streamlit
    if errorlevel 1 (
        echo Error: Failed to install Streamlit
        pause
        exit /b 1
    )
)

echo.
echo ✓ Environment ready. Starting Streamlit...
echo.
echo  Local URL:     http://localhost:8501
echo  Network URL:   http://^<your-ip^>:8501
echo.
echo Streamlit will open in your browser automatically.
echo Press Ctrl+C in this window to stop the server.
echo.

REM Run Streamlit
python -m streamlit run streamlit_app.py --logger.level=warning

pause
