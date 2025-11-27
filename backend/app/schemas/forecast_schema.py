from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class TimeSeriesDataPoint(BaseModel):
    """
    Schema for a single time series data point
    """
    date: datetime
    value: float

class TimeSeriesInput(BaseModel):
    """
    Schema for time series input data
    """
    data: List[TimeSeriesDataPoint]
    forecast_steps: int = 7

class ForecastResult(BaseModel):
    """
    Schema for forecast result
    """
    model_name: str
    forecast: List[float]
    dates: List[datetime]
    metrics: Dict[str, float]
    backtest_results: Optional[Dict[str, Any]] = None
    plot: Optional[str] = None  # Base64 encoded plot image

class ModelEvaluation(BaseModel):
    """
    Schema for model evaluation results
    """
    model_name: str
    mae: float
    mape: float
    params: Optional[Dict[str, Any]] = None

class GridSearchResult(BaseModel):
    """
    Schema for grid search results
    """
    best_model: str
    best_params: Dict[str, Any]
    evaluations: List[ModelEvaluation]

class ReportRequest(BaseModel):
    """
    Schema for report generation request
    """
    format: str  # "csv" or "pdf"
    include_plot: bool = False