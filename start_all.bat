@echo off
echo Starting Run-Rate Forecaster...

echo.
echo 1. Starting Backend Server...
cd backend
start "Backend" python main.py
cd ..

echo.
echo 2. Starting Frontend Server...
cd frontend
start "Frontend" npm run dev
cd ..

echo.
echo Both servers started!
echo Frontend: http://localhost:3000
echo Backend API: http://127.0.0.1:8000
echo Backend Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to exit...
pause >nul