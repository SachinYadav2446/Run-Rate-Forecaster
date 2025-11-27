import pandas as pd
import numpy as np
from typing import Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data validation and preprocessing for time series data
    """
    
    @staticmethod
    def validate_and_clean_data(data: pd.DataFrame, date_column: str, value_column: str) -> pd.DataFrame:
        """
        Validates and cleans time series data
        
        Args:
            data: DataFrame containing time series data
            date_column: Name of the column containing dates
            value_column: Name of the column containing values
            
        Returns:
            Cleaned DataFrame with sorted dates and filled missing values
        """
        # Check if required columns exist
        if date_column not in data.columns:
            raise ValueError(f"Date column '{date_column}' not found in data")
        
        if value_column not in data.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")
        
        # Convert date column to datetime
        try:
            data[date_column] = pd.to_datetime(data[date_column])
        except Exception as e:
            raise ValueError(f"Unable to convert '{date_column}' to datetime: {str(e)}")
        
        # Sort by date
        data = data.sort_values(by=date_column).reset_index(drop=True)
        
        # Set date as index
        data = data.set_index(date_column)
        
        # Convert value column to numeric
        try:
            data[value_column] = pd.to_numeric(data[value_column], errors='coerce')
        except Exception as e:
            raise ValueError(f"Unable to convert '{value_column}' to numeric: {str(e)}")
        
        # Check for any remaining non-numeric values
        if data[value_column].isna().any():
            logger.warning("Found NaN values in data. These will be forward-filled.")
            
        # Handle missing values
        data[value_column] = data[value_column].fillna(method='ffill').fillna(method='bfill')
        
        # Check if we still have data
        if len(data) == 0:
            raise ValueError("No valid data remaining after cleaning")
            
        return data
    
    @staticmethod
    def resample_to_daily(data: pd.DataFrame, value_column: str) -> pd.DataFrame:
        """
        Resamples data to daily frequency
        
        Args:
            data: DataFrame with datetime index
            value_column: Name of the column containing values
            
        Returns:
            DataFrame resampled to daily frequency
        """
        # Resample to daily frequency
        daily_data = data.resample('D').sum()
        
        # Forward-fill any missing values
        daily_data[value_column] = daily_data[value_column].fillna(method='ffill')
        
        return daily_data
    
    @staticmethod
    def detect_outliers(data: pd.DataFrame, value_column: str, threshold: float = 2.0) -> pd.DataFrame:
        """
        Detects outliers using z-score method
        
        Args:
            data: DataFrame with time series data
            value_column: Name of the column containing values
            threshold: Z-score threshold for outlier detection
            
        Returns:
            DataFrame with outlier flag column
        """
        # Calculate z-scores
        data['z_score'] = np.abs((data[value_column] - data[value_column].mean()) / data[value_column].std())
        
        # Flag outliers
        data['is_outlier'] = data['z_score'] > threshold
        
        return data