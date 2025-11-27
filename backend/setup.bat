@echo off
echo Setting up Run-Rate Forecaster Backend...

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the server, run:
echo   python main.py
echo.
echo The API will be available at http://127.0.0.1:8000
echo API documentation at http://127.0.0.1:8000/docs
pause