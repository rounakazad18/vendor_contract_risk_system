@echo off
REM ================================================================
REM  ContractRisk AI Frontend Launcher
REM  Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
REM ================================================================
REM Uses system Python (which has Streamlit + ReportLab installed).
REM The frontend_app.py auto-injects the .venv site-packages so all
REM backend agents, pdfplumber, python-docx etc. are available.

echo.
echo  =====================================================
echo   ContractRisk AI -- Multi-Agent Contract Review UI
echo   Group 2: Gursirat Singh (12326116)
echo            Rounak Azad   (12326217)
echo  =====================================================
echo.
echo  Starting Streamlit frontend...
echo  Open your browser at: http://localhost:8501
echo.

cd /d "%~dp0"
python -m streamlit run frontend_app.py --server.port 8501 --server.headless false

pause
