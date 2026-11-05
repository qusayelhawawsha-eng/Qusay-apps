@echo off
cd /d "%~dp0"
echo Installing tools, please wait...
python -m pip install -r requirements.txt
echo Starting the app...
python -m streamlit run app.py
pause
