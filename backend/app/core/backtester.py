import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from app.models.forecasting_models import (
    ForecastingModel, 
    MovingAverageModel, 
    ExponentialSmoothingModel, 
    NaiveModel, 
    SeasonalNaiveModel,
    LinearRegressionModel,
    calculate_metrics
)
import logging

logger = logging.getLogger(__name__)

class Backtester:
    """
    Performs backtesting of forecasting models
    """
    
    def __init__(self, models: List[ForecastingModel]):
        self.models = models
    
    def backtest_single_model(self, model: ForecastingModel, data: pd.Series, 
                             train_size: float = 0.8, forecast_horizon: int = 7) -> Dict:
        """
        Perform backtesting for a single model
        
        Args:
            model: Forecasting model to test
            data: Time series data
            train_size: Proportion of data to use for training
            forecast_horizon: Number of steps to forecast
            
        Returns:
            Dictionary with backtesting results
        """
        # Split data into train and test
        split_index = int(len(data) * train_size)
        train_data = data.iloc[:split_index]
        test_data = data.iloc[split_index:]
        
        if len(test_data) < forecast_horizon:
            logger.warning("Test data shorter than forecast horizon. Adjusting horizon.")
            forecast_horizon = len(test_data)
        
        if forecast_horizon <= 0:
            return {"mae": float('inf'), "mape": float('inf'), "predictions": []}
        
        try:
            # Fit model on training data
            model.fit(train_data)
            
            # Forecast
            predictions = model.predict(forecast_horizon)
            
            # Get actual values for the forecast period
            actual_values = test_data.iloc[:forecast_horizon]
            
            # Calculate metrics
            metrics = calculate_metrics(actual_values, predictions)
            
            return {
                "mae": metrics["mae"],
                "mape": metrics["mape"],
                "predictions": predictions.tolist(),
                "actual": actual_values.tolist()
            }
        except Exception as e:
            logger.error(f"Backtesting failed for {model.name}: {str(e)}")
            return {"mae": float('inf'), "mape": float('inf'), "predictions": [], "error": str(e)}
    
    def backtest_all_models(self, data: pd.Series, train_size: float = 0.8, 
                           forecast_horizon: int = 7) -> Dict[str, Dict]:
        """
        Perform backtesting for all models
        
        Args:
            data: Time series data
            train_size: Proportion of data to use for training
            forecast_horizon: Number of steps to forecast
            
        Returns:
            Dictionary with backtesting results for all models
        """
        results = {}
        
        for model in self.models:
            logger.info(f"Backtesting {model.name}")
            try:
                model_results = self.backtest_single_model(model, data, train_size, forecast_horizon)
                results[model.name] = model_results
            except Exception as e:
                logger.error(f"Failed to backtest {model.name}: {str(e)}")
                results[model.name] = {"mae": float('inf'), "mape": float('inf'), "predictions": [], "error": str(e)}
        
        return results
    
    def select_best_model(self, backtest_results: Dict[str, Dict]) -> Tuple[str, Dict]:
        """
        Select the best model based on MAE
        
        Args:
            backtest_results: Results from backtesting all models
            
        Returns:
            Tuple of (best_model_name, best_model_results)
        """
        best_model_name = None
        best_mae = float('inf')
        best_results = {}
        
        for model_name, results in backtest_results.items():
            # Skip models with errors
            if "error" in results:
                continue
                
            mae = results.get("mae", float('inf'))
            if mae < best_mae:
                best_mae = mae
                best_model_name = model_name
                best_results = results
        
        if best_model_name is None:
            # If all models failed, return the first one
            best_model_name = list(backtest_results.keys())[0]
            best_results = backtest_results[best_model_name]
        
        return best_model_name, best_results

def create_default_models() -> List[ForecastingModel]:
    """
    Create a list of default forecasting models
    
    Returns:
        List of forecasting models
    """
    models = [
        LinearRegressionModel(),  # Add Linear Regression first (best for trending data)
        MovingAverageModel(window=7),
        ExponentialSmoothingModel(trend='add'),
        NaiveModel(),
        SeasonalNaiveModel(seasonal_period=7)
    ]
    
    return models