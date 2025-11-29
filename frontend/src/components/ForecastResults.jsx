import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './ForecastResults.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ForecastResults = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="forecast-results">
        <div className="loading-spinner"></div>
        <p>Generating forecast...</p>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  // Prepare data for chart
  const prepareChartData = () => {
    const forecastDates = result.dates.map(date => new Date(date).toLocaleDateString());
    const forecastValues = result.forecast;
    
    // If we have historical data in backtest_results, include it
    const historicalData = result.backtest_results && result.backtest_results[result.model_name] 
      ? result.backtest_results[result.model_name].actual || []
      : [];
    
    const datasets = [
      {
        label: 'Forecast',
        data: forecastValues,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ];
    
    // Add historical data if available
    if (historicalData.length > 0) {
      const historicalDates = historicalData.map((_, index) => 
        new Date(new Date(result.dates[0]).getTime() - (historicalData.length - index) * 24 * 60 * 60 * 1000).toLocaleDateString()
      );
      
      datasets.unshift({
        label: 'Historical Data',
        data: historicalData,
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.1,
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      });
      
      return {
        labels: [...historicalDates, ...forecastDates],
        datasets: datasets
      };
    }

    return {
      labels: forecastDates,
      datasets: datasets
    };
  };

  const chartData = prepareChartData();

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Forecast using ${result.model_name}`,
      },
    },
  };

  return (
    <div className="forecast-results">
      <h2>Forecast Results</h2>
      
      <div className="result-summary">
        <div className="result-card">
          <h3>Best Model</h3>
          <p className="model-name">{result.model_name}</p>
        </div>
        
        <div className="result-card">
          <h3>Mean Absolute Error</h3>
          <p className="metric-value">{result.metrics.mae.toFixed(2)}</p>
        </div>
        
        <div className="result-card">
          <h3>Mean Absolute Percentage Error</h3>
          <p className="metric-value">{(result.metrics.mape * 100).toFixed(2)}%</p>
        </div>
      </div>
      
      <div className="forecast-chart">
        <Line data={chartData} options={chartOptions} />
      </div>
      
      <div className="forecast-table">
        <h3>Forecast Data</h3>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Forecast Value</th>
            </tr>
          </thead>
          <tbody>
            {result.dates.map((date, index) => (
              <tr key={index}>
                <td>{new Date(date).toLocaleDateString()}</td>
                <td>{result.forecast[index].toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ForecastResults;