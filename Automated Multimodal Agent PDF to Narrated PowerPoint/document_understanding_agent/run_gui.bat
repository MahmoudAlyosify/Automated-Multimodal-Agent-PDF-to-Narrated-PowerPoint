@echo off
cd /d "d:\Automated Multimodal Agent PDF to Narrated PowerPoint\document_understanding_agent"
echo Starting Document Understanding Agent GUI...
echo.
echo Opening Streamlit at http://localhost:8501
echo.
python -m streamlit run streamlit_app.py
pause
