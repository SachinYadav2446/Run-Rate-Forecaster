import React, { useState } from 'react';
import axios from 'axios';
import ErrorToast from './ErrorToast';
import './CSVUpload.css';

const CSVUpload = ({ setForecastResult, setLoading, loading }) => {
  const [file, setFile] = useState(null);
  const [forecastSteps, setForecastSteps] = useState(7);
  const [useGridSearch, setUseGridSearch] = useState(false);
  const [toast, setToast] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (selectedFile) => {
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        setToast({ message: 'Please upload a CSV file', type: 'error' });
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setToast({ message: 'File selected successfully!', type: 'success' });
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileChange(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setToast({ message: 'Please select a CSV file before submitting', type: 'warning' });
      return;
    }

    setLoading(true);
    setToast(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Use the backend URL from environment variables
      const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const url = `${baseUrl}/upload-csv?forecast_steps=${forecastSteps}&use_grid_search=${useGridSearch}`;

      const response = await axios.post(
        url,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setForecastResult(response.data);
      setToast({ message: 'Forecast generated successfully! 🎉', type: 'success' });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to process CSV file. Please check your data format.';
      setToast({ message: errorMsg, type: 'error' });
      console.error('CSV upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadSampleCSV = () => {
    // Generate sample data with realistic time series pattern
    let csvContent = 'date,value\n';
    const startDate = new Date('2022-01-01');
    let baseValue = 100;
    
    for (let i = 0; i < 1000; i++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);
      const dateStr = currentDate.toISOString().split('T')[0];
      
      // Add some variation to make it realistic
      const variation = Math.floor(Math.random() * 10) - 2;
      baseValue += variation;
      
      csvContent += `${dateStr},${baseValue}\n`;
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_data_1000_points.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    setToast({ message: 'Sample CSV with 1000 data points downloaded! 📥', type: 'success' });
  };

  return (
    <div className="csv-upload">
      {toast && (
        <ErrorToast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          duration={5000}
        />
      )}
      <h2>Upload CSV File</h2>
      <form onSubmit={handleSubmit}>
        
        <div className="upload-section">
          <div 
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('csv-file').click()}
          >
            <input
              type="file"
              id="csv-file"
              accept=".csv"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />
            {file ? (
              <>
                <span className="file-icon">📄</span>
                <p className="file-name">{file.name}</p>
                <p className="file-size">({(file.size / 1024).toFixed(2)} KB)</p>
              </>
            ) : (
              <>
                <span className="upload-icon">📤</span>
                <p>Drag and drop your CSV file here</p>
                <p className="or-text">or</p>
                <button 
                  type="button" 
                  className="btn btn-secondary browse-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    document.getElementById('csv-file').click();
                  }}
                >
                  Browse Files
                </button>
              </>
            )}
          </div>
          
          <div className="csv-info">
            <h4>📋 CSV Format Requirements:</h4>
            <ul>
              <li>✅ Must have 'date' and 'value' columns</li>
              <li>📅 Date format: YYYY-MM-DD (e.g., 2024-01-15)</li>
              <li>🔢 Value must be numeric (integers or decimals)</li>
              <li>🚫 No missing values in required columns</li>
              <li>📊 Supports large datasets (1000+ data points)</li>
            </ul>
            <button type="button" className="btn-link" onClick={downloadSampleCSV}>
              📥 Download Sample CSV (1000 data points)
            </button>
            <a 
              href="/complex_volatile_data_10000_full.csv" 
              download="complex_volatile_data_10000_full.csv"
              className="btn-link"
              style={{ marginTop: '10px', display: 'inline-block' }}
            >
              📥 Download Complex Volatile Dataset (10,000 data points)
            </a>
            <p style={{ fontSize: '0.9em', marginTop: '10px', color: '#666' }}>
              The complex dataset contains multiple patterns that prevent straight-line forecasts.
            </p>
          </div>
        </div>

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
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading || !file}
          >
            {loading ? 'Processing...' : 'Generate Forecast'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CSVUpload;