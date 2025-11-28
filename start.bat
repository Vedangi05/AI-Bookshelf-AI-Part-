@echo off
REM Start both Flask backend and Streamlit frontend for local testing

echo.
echo ========================================
echo AI-Bookshelf RAG - Starting services
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo Error: Virtual environment not found. Run setup.bat first.
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Start Flask backend using waitress (Windows compatible)
echo Starting Flask backend on http://127.0.0.1:5000 using waitress
start "Flask Backend - AI-Bookshelf RAG" cmd /k "waitress-serve --listen=*:5000 main:app"

echo.
echo ========================================
echo Service starting...
echo ========================================
echo Flask: http://127.0.0.1:5000
echo.
echo Press Ctrl+C in the Flask window to stop
echo.
