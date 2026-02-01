#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Streamlit GUI Launcher for PDF-to-Narrated-PowerPoint System
    
.DESCRIPTION
    This script starts the Streamlit web interface for the PDF-to-PowerPoint converter
    
.EXAMPLE
    .\run_gui.ps1
#>

# Display header
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PDF-to-Narrated-PowerPoint Converter - Streamlit GUI         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
Set-Location $scriptDir

Write-Host "Starting Streamlit application..." -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check and install Streamlit if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$streamlitCheck = python -m pip show streamlit 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Streamlit..." -ForegroundColor Yellow
    python -m pip install streamlit
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install Streamlit" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "✓ Environment ready. Starting Streamlit..." -ForegroundColor Green
Write-Host ""
Write-Host "  Local URL:     http://localhost:8501" -ForegroundColor Cyan
Write-Host "  Network URL:   http://<your-ip>:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Streamlit will open in your browser automatically." -ForegroundColor Green
Write-Host "Press Ctrl+C in this window to stop the server." -ForegroundColor Green
Write-Host ""

# Run Streamlit
python -m streamlit run streamlit_app.py --logger.level=warning

Read-Host "Press Enter to exit"
