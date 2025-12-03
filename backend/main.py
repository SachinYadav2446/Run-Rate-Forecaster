"""
Main entry point for the Run-Rate Forecaster application
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Run the application
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)