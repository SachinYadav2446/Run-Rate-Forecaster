# Run-Rate Forecaster

A complete time-series forecasting system with a React frontend and FastAPI backend.

## 📁 Project Structure

```
run-rate-forecaster/
├── backend/
│   ├── app/
│   │   ├── core/           # Core business logic
│   │   ├── models/         # Forecasting models
│   │   ├── schemas/        # Pydantic models
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # Application entry point
├── frontend/
│   ├── public/            # Static assets
│   ├── src/               # React source code
│   │   ├── components/    # React components
│   │   ├── assets/        # Images and other assets
│   │   ├── App.jsx        # Main App component
│   │   ├── App.css        # App styles
│   │   ├── main.jsx       # React entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # Frontend dependencies
│   └── vite.config.js     # Vite configuration
└── README.md              # This file
```

## 🚀 Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python main.py
   ```
   
   The backend will be available at http://127.0.0.1:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at http://localhost:3000

## 🌐 API Endpoints

The backend provides the following endpoints:

- `POST /forecast` - Forecast with automatic model selection
- `POST /forecast-with-grid-search` - Forecast with grid search optimization

## 🎨 UI Features

The React frontend provides:

- Intuitive data input form
- Real-time forecast visualization
- Performance metrics display
- Responsive design for all devices
- Grid search optimization option

## 🛠️ Development

### Backend Development

The backend is built with:
- FastAPI for the REST API
- Pandas and NumPy for data processing
- Statsmodels for forecasting algorithms
- Scikit-learn for metrics calculation

### Frontend Development

The frontend is built with:
- React for the UI components
- Vite for fast development
- Chart.js for data visualization
- Axios for API communication

## 📈 Usage

1. Start both the backend and frontend servers
2. Open http://localhost:3000 in your browser
3. Enter your time-series data in the form
4. Choose forecast parameters
5. Click "Get Forecast" to see predictions