# Run Streamlit GUI for Document Understanding Agent
Write-Host "Starting Document Understanding Agent GUI..." -ForegroundColor Green
Write-Host "Opening browser at http://localhost:8501" -ForegroundColor Cyan

venv\Scripts\streamlit.exe run streamlit_app.py --logger.level=warning
