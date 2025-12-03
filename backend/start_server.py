"""
Startup script for the Run-Rate Forecaster
"""

import subprocess
import sys
import os

def install_dependencies():
    """
    Install required dependencies
    """
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def start_server():
    """
    Start the FastAPI server
    """
    print("Starting Run-Rate Forecaster server...")
    print("Server will be available at http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    
    try:
        # Start the server
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    print("Run-Rate Forecaster Startup Script")
    print("=" * 40)
    
    # Check if dependencies are installed
    try:
        import fastapi
        import pandas
        import numpy
        import statsmodels
        print("Dependencies already installed.")
    except ImportError:
        # Install dependencies
        if not install_dependencies():
            print("Failed to install dependencies. Exiting.")
            sys.exit(1)
    
    # Start the server
    start_server()