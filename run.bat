@echo off
REM Quick Start Script for Streamlit AI Nutritionist Testing UI

echo ===============================================
echo AI Nutritionist Chat - Streamlit Testing UI
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo [2/3] Checking backend connection...
echo.
echo ⚠️  Make sure the Go backend is running at http://localhost:8080
echo    In another terminal, run: go run main.go
echo.
pause

echo [3/3] Starting Streamlit app...
echo.
echo 🚀 Opening http://localhost:8501
echo    (Press Ctrl+C in this window to stop)
echo.
streamlit run app.py

pause
