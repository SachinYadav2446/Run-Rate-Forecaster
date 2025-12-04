import React, { useState } from 'react';
import axios from 'axios';
import ErrorToast from './ErrorToast';
import './ForecastForm.css';

const ForecastForm = ({ setForecastResult, setLoading, loading }) => {
  const [dataPoints, setDataPoints] = useState([
    { date: '', value: '' },
    { date: '', value: '' },
    { date: '', value: '' }
  ]);
  const [forecastSteps, setForecastSteps] = useState(7);
  const [toast, setToast] = useState(null);
  const [useGridSearch, setUseGridSearch] = useState(false);

  const handleDataPointChange = (index, field, value) => {
    const newDataPoints = [...dataPoints];
    newDataPoints[index][field] = value;
    setDataPoints(newDataPoints);
  };

  const addDataPoint = () => {
    setDataPoints([...dataPoints, { date: '', value: '' }]);
  };

  const removeDataPoint = (index) => {
    if (dataPoints.length > 1) {
      const newDataPoints = [...dataPoints];
      newDataPoints.splice(index, 1);
      setDataPoints(newDataPoints);
    }
  };

  const validateData = () => {
    // Check if we have at least 2 data points
    if (dataPoints.length < 2) {
      setToast({ message: 'Please add at least 2 data points', type: 'error' });
      return false;
    }

    // Check if all data points have values
    for (let i = 0; i < dataPoints.length; i++) {
      const point = dataPoints[i];
      if (!point.date || !point.value) {
        setToast({ message: `Please fill in both date and value for data point ${i + 1}`, type: 'error' });
        return false;
      }
      
      // Validate date format
      if (!/^\d{4}-\d{2}-\d{2}/.test(point.date)) {
        setToast({ message: `Please enter a valid date for data point ${i + 1} (YYYY-MM-DD)`, type: 'error' });
        return false;
      }
      
      // Validate numeric value
      if (isNaN(parseFloat(point.value))) {
        setToast({ message: `Please enter a valid number for value in data point ${i + 1}`, type: 'error' });
        return false;
      }
    }

    setToast(null);
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateData()) {
      return;
    }

    setLoading(true);
    setToast(null);

    try {
      // Format data for API
      const formattedData = dataPoints.map(point => ({
        date: new Date(point.date).toISOString(),
        value: parseFloat(point.value)
      }));

      const payload = {
        data: formattedData,
        forecast_steps: parseInt(forecastSteps)
      };

      // Determine which endpoint to use
      const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const endpoint = useGridSearch 
        ? `${baseUrl}/forecast-with-grid-search` 
        : `${baseUrl}/forecast`;

      const response = await axios.post(endpoint, payload);
      
      setForecastResult(response.data);
      setToast({ message: 'Forecast generated successfully! 🎉', type: 'success' });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to get forecast. Please check your data and try again.';
      setToast({ message: errorMsg, type: 'error' });
      console.error('Forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forecast-form">
      {toast && (
        <ErrorToast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          duration={5000}
        />
      )}
      <h2>Enter Time-Series Data</h2>
      <form onSubmit={handleSubmit}>
        
        <div className="form-options">
          <div className="form-group">
            <label className="form-label">
              <input
                type="checkbox"
                checked={useGridSearch}
                onChange={(e) => setUseGridSearch(e.target.checked)}
              />
              Use Grid Search Optimization
            </label>
          </div>
          
          <div className="form-group">
            <label className="form-label">Forecast Steps:</label>
            <input
              type="number"
              className="form-input"
              value={forecastSteps}
              onChange={(e) => setForecastSteps(e.target.value)}
              min="1"
              max="365"
            />
          </div>
        </div>

        <div className="data-points">
          <h3>Data Points</h3>
          {dataPoints.map((point, index) => (
            <div key={index} className="data-point-row">
              <div className="form-group">
                <label className="form-label">Date {index + 1}:</label>
                <input
                  type="date"
                  className="form-input"
                  value={point.date}
                  onChange={(e) => handleDataPointChange(index, 'date', e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Value {index + 1}:</label>
                <input
                  type="number"
                  className="form-input"
                  value={point.value}
                  onChange={(e) => handleDataPointChange(index, 'value', e.target.value)}
                  step="0.01"
                />
              </div>
              
              {dataPoints.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => removeDataPoint(index)}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
        
        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={addDataPoint}>
            Add Data Point
          </button>
          
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
          >
            {loading ? 'Predicting...' : 'Get Forecast'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ForecastForm;