import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

class ForecastingModel:
    """
    Base class for forecasting models
    """
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.fitted = False
    
    def fit(self, data: pd.Series):
        """
        Fit the model to the data
        """
        raise NotImplementedError
    
    def predict(self, steps: int) -> pd.Series:
        """
        Make predictions for the specified number of steps
        """
        raise NotImplementedError
    
    def forecast(self, data: pd.Series, steps: int) -> pd.Series:
        """
        Fit the model and make predictions
        """
        self.fit(data)
        return self.predict(steps)

class MovingAverageModel(ForecastingModel):
    """
    Moving Average Model with trend extrapolation
    """
    
    def __init__(self, window: int = 7):
        super().__init__("Moving Average")
        self.window = window
    
    def fit(self, data: pd.Series):
        """
        Fit the moving average model and calculate trend
        """
        self.data = data
        self.fitted = True
        
        # Calculate trend from recent data
        recent_data = data.iloc[-min(30, len(data)):]
        if len(recent_data) > 1:
            x = np.arange(len(recent_data)).reshape(-1, 1)
            y = recent_data.values
            lr = LinearRegression()
            lr.fit(x, y)
            self.trend_slope = lr.coef_[0]
        else:
            self.trend_slope = 0
    
    def predict(self, steps: int) -> pd.Series:
        """
        Predict using moving average with trend extrapolation
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Calculate the moving average of the last 'window' values
        last_values = self.data.iloc[-self.window:].values
        avg_value = np.mean(last_values)
        
        # Create forecast with trend
        forecast_values = [avg_value + (i + 1) * self.trend_slope for i in range(steps)]
        
        # Create forecast index
        last_date = self.data.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='D')
        
        return pd.Series(forecast_values, index=forecast_dates)

class ExponentialSmoothingModel(ForecastingModel):
    """
    Exponential Smoothing Model
    """
    
    def __init__(self, trend: Optional[str] = 'add', seasonal: Optional[str] = None, seasonal_periods: Optional[int] = None):
        super().__init__("Exponential Smoothing")
        self.trend = trend
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods
    
    def fit(self, data: pd.Series):
        """
        Fit the exponential smoothing model
        """
        try:
            self.model = ExponentialSmoothing(
                data,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods
            )
            self.fitted_model = self.model.fit()
            self.fitted = True
        except Exception as e:
            logger.error(f"Failed to fit Exponential Smoothing model: {str(e)}")
            # Fallback to simple model
            self.model = ExponentialSmoothing(data)
            self.fitted_model = self.model.fit()
            self.fitted = True
    
    def predict(self, steps: int) -> pd.Series:
        """
        Predict using the fitted exponential smoothing model
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        forecast = self.fitted_model.forecast(steps)
        return forecast

class NaiveModel(ForecastingModel):
    """
    Naive Model - predicts the last observed value
    """
    
    def __init__(self):
        super().__init__("Naive")
    
    def fit(self, data: pd.Series):
        """
        For naive model, fitting is just storing the last value
        """
        self.last_value = data.iloc[-1]
        self.data = data
        self.fitted = True
    
    def predict(self, steps: int) -> pd.Series:
        """
        Predict using the last observed value
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Create forecast index
        last_date = self.data.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='D')
        
        # Return constant forecast with last value
        return pd.Series([self.last_value] * steps, index=forecast_dates)

class SeasonalNaiveModel(ForecastingModel):
    """
    Seasonal Naive Model - predicts the value from the same season in the previous cycle
    """
    
    def __init__(self, seasonal_period: int = 7):
        super().__init__("Seasonal Naive")
        self.seasonal_period = seasonal_period
    
    def fit(self, data: pd.Series):
        """
        For seasonal naive model, store the data
        """
        self.data = data
        self.fitted = True
    
    def predict(self, steps: int) -> pd.Series:
        """
        Predict using seasonal naive approach
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Create forecast index
        last_date = self.data.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='D')
        
        # Get seasonal values from the same period in previous cycles
        predictions = []
        for i in range(steps):
            # Find the corresponding seasonal value
            seasonal_index = -self.seasonal_period + (i % self.seasonal_period)
            seasonal_value = self.data.iloc[seasonal_index]
            predictions.append(seasonal_value)
        
        return pd.Series(predictions, index=forecast_dates)

class LinearRegressionModel(ForecastingModel):
    """
    Linear Regression Model for trend forecasting
    """
    
    def __init__(self):
        super().__init__("Linear Regression")
        self.model = LinearRegression()
    
    def fit(self, data: pd.Series):
        """
        Fit linear regression model to capture trend
        """
        self.data = data
        # Create time index as feature
        X = np.arange(len(data)).reshape(-1, 1)
        y = data.values
        
        self.model.fit(X, y)
        self.fitted = True
    
    def predict(self, steps: int) -> pd.Series:
        """
        Predict using linear regression trend
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Create future time indices
        start_index = len(self.data)
        X_future = np.arange(start_index, start_index + steps).reshape(-1, 1)
        
        # Make predictions
        predictions = self.model.predict(X_future)
        
        # Create forecast index
        last_date = self.data.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='D')
        
        return pd.Series(predictions, index=forecast_dates)

def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """
    Calculate forecasting metrics (MAE and MAPE)
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        Dictionary with MAE and MAPE values
    """
    # Align series to same index
    aligned_actual, aligned_predicted = actual.align(predicted, join='inner')
    
    # Remove any NaN values
    mask = ~(np.isnan(aligned_actual) | np.isnan(aligned_predicted))
    aligned_actual = aligned_actual[mask]
    aligned_predicted = aligned_predicted[mask]
    
    if len(aligned_actual) == 0:
        return {"mae": float('inf'), "mape": float('inf')}
    
    mae = mean_absolute_error(aligned_actual, aligned_predicted)
    
    # Handle case where actual values contain zeros
    if (aligned_actual == 0).any():
        # Add small epsilon to avoid division by zero
        aligned_actual = aligned_actual.replace(0, 1e-10)
    
    mape = mean_absolute_percentage_error(aligned_actual, aligned_predicted)
    
    return {"mae": mae, "mape": mape}