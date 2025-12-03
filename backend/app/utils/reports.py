import pandas as pd
import csv
import io
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

def generate_csv_report(data: Dict[str, Any], filename: str = "forecast_report.csv") -> str:
    """
    Generate a CSV report of the forecast results
    
    Args:
        data: Forecast results data
        filename: Name of the CSV file
        
    Returns:
        Path to the generated CSV file
    """
    try:
        # Create DataFrame from forecast data
        forecast_df = pd.DataFrame({
            'date': data.get('dates', []),
            'forecast': data.get('forecast', [])
        })
        
        # Save to CSV
        csv_buffer = io.StringIO()
        forecast_df.to_csv(csv_buffer, index=False)
        
        # Write to file
        with open(filename, 'w', newline='') as csvfile:
            csvfile.write(csv_buffer.getvalue())
        
        return filename
        
    except Exception as e:
        logger.error(f"Failed to generate CSV report: {str(e)}")
        return ""

def generate_detailed_report(backtest_results: Dict[str, Any], 
                           best_model: str, 
                           filename: str = "detailed_report.csv") -> str:
    """
    Generate a detailed CSV report with backtest results for all models
    
    Args:
        backtest_results: Results from backtesting all models
        best_model: Name of the best performing model
        filename: Name of the CSV file
        
    Returns:
        Path to the generated CSV file
    """
    try:
        # Prepare data for CSV
        report_data = []
        
        for model_name, results in backtest_results.items():
            report_data.append({
                'model': model_name,
                'mae': results.get('mae', 'N/A'),
                'mape': results.get('mape', 'N/A'),
                'is_best': 'Yes' if model_name == best_model else 'No'
            })
        
        # Create DataFrame
        report_df = pd.DataFrame(report_data)
        
        # Save to CSV
        report_df.to_csv(filename, index=False)
        
        return filename
        
    except Exception as e:
        logger.error(f"Failed to generate detailed report: {str(e)}")
        return ""

def export_time_series_data(data: pd.Series, filename: str = "time_series_data.csv") -> str:
    """
    Export time series data to CSV
    
    Args:
        data: Time series data
        filename: Name of the CSV file
        
    Returns:
        Path to the generated CSV file
    """
    try:
        # Create DataFrame
        df = pd.DataFrame({
            'date': data.index,
            'value': data.values
        })
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        return filename
        
    except Exception as e:
        logger.error(f"Failed to export time series data: {str(e)}")
        return ""