import pandas as pd
from typing import Dict, List, Tuple, Any
from app.models.forecasting_models import (
    MovingAverageModel, 
    ExponentialSmoothingModel, 
    NaiveModel, 
    SeasonalNaiveModel
)
from app.core.backtester import Backtester
import logging
import itertools

logger = logging.getLogger(__name__)

class GridSearchOptimizer:
    """
    Performs grid search to find the best model parameters
    """
    
    def __init__(self):
        self.param_grids = {
            "Moving Average": {
                "window": [3, 5, 7, 14, 30]
            },
            "Exponential Smoothing": {
                "trend": ['add', 'mul', None],
                "seasonal": [None, 'add', 'mul'],
                "seasonal_periods": [None, 7, 12, 30]
            },
            "Naive": {},
            "Seasonal Naive": {
                "seasonal_period": [3, 5, 7, 12, 30]
            }
        }
    
    def generate_param_combinations(self, model_name: str) -> List[Dict]:
        """
        Generate all parameter combinations for a given model
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of parameter dictionaries
        """
        if model_name not in self.param_grids:
            return [{}]
        
        param_grid = self.param_grids[model_name]
        
        # Handle empty parameter grids
        if not param_grid:
            return [{}]
        
        # Generate all combinations
        keys = param_grid.keys()
        values = param_grid.values()
        
        # Handle None values in parameter grid
        processed_values = []
        for val_list in values:
            processed_values.append([v for v in val_list if v is not None or len(val_list) == 1 or v is not None])
        
        combinations = list(itertools.product(*processed_values))
        
        # Convert to list of dictionaries
        param_combinations = []
        for combination in combinations:
            param_dict = dict(zip(keys, combination))
            param_combinations.append(param_dict)
        
        return param_combinations
    
    def create_model_with_params(self, model_name: str, params: Dict) -> Any:
        """
        Create a model instance with specified parameters
        
        Args:
            model_name: Name of the model
            params: Dictionary of parameters
            
        Returns:
            Model instance
        """
        if model_name == "Moving Average":
            window = params.get("window", 7)
            return MovingAverageModel(window=window)
        elif model_name == "Exponential Smoothing":
            return ExponentialSmoothingModel(
                trend=params.get("trend", None),
                seasonal=params.get("seasonal", None),
                seasonal_periods=params.get("seasonal_periods", None)
            )
        elif model_name == "Naive":
            return NaiveModel()
        elif model_name == "Seasonal Naive":
            seasonal_period = params.get("seasonal_period", 7)
            return SeasonalNaiveModel(seasonal_period=seasonal_period)
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def grid_search(self, data: pd.Series, model_name: str, 
                   train_size: float = 0.8, forecast_horizon: int = 7) -> Tuple[Dict, float]:
        """
        Perform grid search for a specific model type
        
        Args:
            data: Time series data
            model_name: Name of the model to optimize
            train_size: Proportion of data to use for training
            forecast_horizon: Number of steps to forecast
            
        Returns:
            Tuple of (best_params, best_mae)
        """
        param_combinations = self.generate_param_combinations(model_name)
        
        best_params = {}
        best_mae = float('inf')
        
        logger.info(f"Performing grid search for {model_name} with {len(param_combinations)} parameter combinations")
        
        for i, params in enumerate(param_combinations):
            try:
                # Create model with parameters
                model = self.create_model_with_params(model_name, params)
                
                # Create backtester with single model
                backtester = Backtester([model])
                
                # Perform backtesting
                results = backtester.backtest_single_model(model, data, train_size, forecast_horizon)
                
                mae = results.get("mae", float('inf'))
                
                if mae < best_mae:
                    best_mae = mae
                    best_params = params
                    
                logger.debug(f"Params {params}: MAE = {mae}")
                
            except Exception as e:
                logger.warning(f"Failed to test parameters {params} for {model_name}: {str(e)}")
                continue
        
        return best_params, best_mae
    
    def optimize_all_models(self, data: pd.Series, train_size: float = 0.8, 
                          forecast_horizon: int = 7) -> Dict[str, Tuple[Dict, float]]:
        """
        Perform grid search optimization for all model types
        
        Args:
            data: Time series data
            train_size: Proportion of data to use for training
            forecast_horizon: Number of steps to forecast
            
        Returns:
            Dictionary mapping model names to (best_params, best_mae)
        """
        results = {}
        
        for model_name in self.param_grids.keys():
            try:
                logger.info(f"Optimizing {model_name}")
                best_params, best_mae = self.grid_search(data, model_name, train_size, forecast_horizon)
                results[model_name] = (best_params, best_mae)
            except Exception as e:
                logger.error(f"Failed to optimize {model_name}: {str(e)}")
                results[model_name] = ({}, float('inf'))
        
        return results