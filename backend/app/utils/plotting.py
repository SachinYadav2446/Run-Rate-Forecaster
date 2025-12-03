import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

def plot_forecast(actual_data: pd.Series, forecast_data: pd.Series, 
                 title: str = "Time Series Forecast") -> str:
    """
    Plot actual data and forecast
    
    Args:
        actual_data: Actual time series data
        forecast_data: Forecasted data
        title: Plot title
        
    Returns:
        Base64 encoded plot image
    """
    try:
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot actual data
        plt.plot(actual_data.index, actual_data.values, label='Actual', color='blue')
        
        # Plot forecast
        plt.plot(forecast_data.index, forecast_data.values, label='Forecast', color='red', linestyle='--')
        
        # Formatting
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode to base64
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Close figure to free memory
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        logger.error(f"Failed to create plot: {str(e)}")
        return ""

def plot_model_comparison(model_results: dict, title: str = "Model Comparison") -> str:
    """
    Plot comparison of different model performances
    
    Args:
        model_results: Dictionary with model results
        title: Plot title
        
    Returns:
        Base64 encoded plot image
    """
    try:
        # Extract model names and MAE values
        models = []
        mae_values = []
        
        for model_name, results in model_results.items():
            if "mae" in results and results["mae"] != float('inf'):
                models.append(model_name)
                mae_values.append(results["mae"])
        
        if not models:
            return ""
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(models, mae_values, color='skyblue')
        
        # Add value labels on bars
        for bar, value in zip(bars, mae_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}', ha='center', va='bottom')
        
        # Formatting
        plt.title(title)
        plt.xlabel('Models')
        plt.ylabel('MAE (Mean Absolute Error)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode to base64
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Close figure to free memory
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        logger.error(f"Failed to create model comparison plot: {str(e)}")
        return ""