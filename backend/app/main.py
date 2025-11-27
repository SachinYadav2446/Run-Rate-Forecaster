import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import io

from app.schemas.forecast_schema import TimeSeriesInput, ForecastResult, ReportRequest
from app.core.data_processor import DataProcessor
from app.models.forecasting_models import calculate_metrics
from app.core.backtester import Backtester, create_default_models
from app.core.grid_search import GridSearchOptimizer
from app.utils.plotting import plot_forecast, plot_model_comparison
from app.utils.reports import generate_csv_report, generate_detailed_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Run-Rate Forecaster",
    description="A time-series forecasting system with classical models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to Run-Rate Forecaster API"}

@app.post("/forecast", response_model=ForecastResult)
async def forecast_time_series(input_data: TimeSeriesInput):
    """
    Forecast time series data using the best performing model
    
    Args:
        input_data: Time series data and forecast parameters
        
    Returns:
        Forecast results with predictions and accuracy metrics
    """
    try:
        # Convert input data to DataFrame
        df_data = pd.DataFrame([
            {"date": point.date, "value": point.value} 
            for point in input_data.data
        ])
        
        # Validate and clean data
        processor = DataProcessor()
        cleaned_data = processor.validate_and_clean_data(df_data, "date", "value")
        
        # Extract time series
        time_series = cleaned_data["value"]
        
        # Create models
        models = create_default_models()
        
        # Perform backtesting
        backtester = Backtester(models)
        backtest_results = backtester.backtest_all_models(time_series, train_size=0.8, 
                                                         forecast_horizon=input_data.forecast_steps)
        
        # Select best model
        best_model_name, best_results = backtester.select_best_model(backtest_results)
        
        # Create the best model instance
        if best_model_name == "Linear Regression":
            from app.models.forecasting_models import LinearRegressionModel
            best_model = LinearRegressionModel()
        elif best_model_name == "Moving Average":
            from app.models.forecasting_models import MovingAverageModel
            best_model = MovingAverageModel(window=7)
        elif best_model_name == "Exponential Smoothing":
            from app.models.forecasting_models import ExponentialSmoothingModel
            best_model = ExponentialSmoothingModel(trend='add')
        elif best_model_name == "Naive":
            from app.models.forecasting_models import NaiveModel
            best_model = NaiveModel()
        elif best_model_name == "Seasonal Naive":
            from app.models.forecasting_models import SeasonalNaiveModel
            best_model = SeasonalNaiveModel(seasonal_period=7)
        else:
            raise ValueError(f"Unknown model: {best_model_name}")
        
        # Fit the best model on all data and forecast
        best_model.fit(time_series)
        forecast = best_model.predict(input_data.forecast_steps)
        
        # Create plot
        plot_base64 = plot_forecast(time_series, forecast, f"Forecast using {best_model_name}")
        
        # Prepare response
        result = ForecastResult(
            model_name=best_model_name,
            forecast=forecast.tolist(),
            dates=forecast.index.tolist(),
            metrics={
                "mae": best_results.get("mae", float('inf')),
                "mape": best_results.get("mape", float('inf'))
            },
            backtest_results=backtest_results,
            plot=plot_base64
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Forecasting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")

@app.post("/forecast-with-grid-search", response_model=ForecastResult)
async def forecast_with_grid_search(input_data: TimeSeriesInput):
    """
    Forecast time series data using grid search to optimize model parameters
    
    Args:
        input_data: Time series data and forecast parameters
        
    Returns:
        Forecast results with predictions and accuracy metrics
    """
    try:
        # Convert input data to DataFrame
        df_data = pd.DataFrame([
            {"date": point.date, "value": point.value} 
            for point in input_data.data
        ])
        
        # Validate and clean data
        processor = DataProcessor()
        cleaned_data = processor.validate_and_clean_data(df_data, "date", "value")
        
        # Extract time series
        time_series = cleaned_data["value"]
        
        # Perform grid search optimization
        optimizer = GridSearchOptimizer()
        optimization_results = optimizer.optimize_all_models(time_series, train_size=0.8, 
                                                           forecast_horizon=input_data.forecast_steps)
        
        # Find the best model overall
        best_model_name = None
        best_mae = float('inf')
        best_params = {}
        
        for model_name, (params, mae) in optimization_results.items():
            if mae < best_mae:
                best_mae = mae
                best_model_name = model_name
                best_params = params
        
        # Create the best model with optimized parameters
        if best_model_name == "Linear Regression":
            from app.models.forecasting_models import LinearRegressionModel
            best_model = LinearRegressionModel()
        elif best_model_name == "Moving Average":
            from app.models.forecasting_models import MovingAverageModel
            window = best_params.get("window", 7)
            best_model = MovingAverageModel(window=window)
        elif best_model_name == "Exponential Smoothing":
            from app.models.forecasting_models import ExponentialSmoothingModel
            best_model = ExponentialSmoothingModel(
                trend=best_params.get("trend", None),
                seasonal=best_params.get("seasonal", None),
                seasonal_periods=best_params.get("seasonal_periods", None)
            )
        elif best_model_name == "Naive":
            from app.models.forecasting_models import NaiveModel
            best_model = NaiveModel()
        elif best_model_name == "Seasonal Naive":
            from app.models.forecasting_models import SeasonalNaiveModel
            seasonal_period = best_params.get("seasonal_period", 7)
            best_model = SeasonalNaiveModel(seasonal_period=seasonal_period)
        else:
            raise ValueError(f"Unknown model: {best_model_name}")
        
        # Perform backtesting with the best model
        backtester = Backtester([best_model])
        backtest_results = backtester.backtest_single_model(best_model, time_series, 
                                                           train_size=0.8, 
                                                           forecast_horizon=input_data.forecast_steps)
        
        # Fit the best model on all data and forecast
        best_model.fit(time_series)
        forecast = best_model.predict(input_data.forecast_steps)
        
        # Create plot
        plot_base64 = plot_forecast(time_series, forecast, f"Forecast using {best_model_name} (Grid Search)")
        
        # Prepare response
        result = ForecastResult(
            model_name=best_model_name,
            forecast=forecast.tolist(),
            dates=forecast.index.tolist(),
            metrics={
                "mae": backtest_results.get("mae", float('inf')),
                "mape": backtest_results.get("mape", float('inf'))
            },
            plot=plot_base64
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Grid search forecasting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grid search forecasting failed: {str(e)}")

@app.post("/generate-report")
async def generate_report(input_data: TimeSeriesInput, report_request: ReportRequest):
    """
    Generate a report (CSV/PDF) of the forecast results
    
    Args:
        input_data: Time series data and forecast parameters
        report_request: Report generation parameters
        
    Returns:
        File response with the generated report
    """
    try:
        # First, generate forecast results
        forecast_result = await forecast_time_series(input_data)
        
        if report_request.format.lower() == "csv":
            # Generate CSV report
            filename = generate_csv_report(forecast_result.dict(), "forecast_report.csv")
            if filename:
                return FileResponse(filename, media_type='text/csv', filename='forecast_report.csv')
            else:
                raise HTTPException(status_code=500, detail="Failed to generate CSV report")
        else:
            raise HTTPException(status_code=400, detail="Unsupported report format. Use 'csv'.")
            
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/upload-csv", response_model=ForecastResult)
async def upload_csv(file: UploadFile = File(...), forecast_steps: int = 7, use_grid_search: bool = False):
    """
    Upload a CSV file with time-series data and get forecast
    
    Args:
        file: CSV file with 'date' and 'value' columns
        forecast_steps: Number of future steps to forecast
        use_grid_search: Whether to use grid search optimization
        
    Returns:
        Forecast results with predictions and accuracy metrics
    """
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        if 'date' not in df.columns or 'value' not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must have 'date' and 'value' columns"
            )
        
        # Convert to required format
        df_data = df[['date', 'value']].copy()
        
        # Validate and clean data
        processor = DataProcessor()
        cleaned_data = processor.validate_and_clean_data(df_data, "date", "value")
        
        # Extract time series
        time_series = cleaned_data["value"]
        
        if use_grid_search:
            # Perform grid search optimization
            optimizer = GridSearchOptimizer()
            optimization_results = optimizer.optimize_all_models(time_series, train_size=0.8, 
                                                               forecast_horizon=forecast_steps)
            
            # Find the best model overall
            best_model_name = None
            best_mae = float('inf')
            best_params = {}
            
            for model_name, (params, mae) in optimization_results.items():
                if mae < best_mae:
                    best_mae = mae
                    best_model_name = model_name
                    best_params = params
            
            # Create the best model with optimized parameters
            if best_model_name == "Linear Regression":
                from app.models.forecasting_models import LinearRegressionModel
                best_model = LinearRegressionModel()
            elif best_model_name == "Moving Average":
                from app.models.forecasting_models import MovingAverageModel
                window = best_params.get("window", 7)
                best_model = MovingAverageModel(window=window)
            elif best_model_name == "Exponential Smoothing":
                from app.models.forecasting_models import ExponentialSmoothingModel
                best_model = ExponentialSmoothingModel(
                    trend=best_params.get("trend", None),
                    seasonal=best_params.get("seasonal", None),
                    seasonal_periods=best_params.get("seasonal_periods", None)
                )
            elif best_model_name == "Naive":
                from app.models.forecasting_models import NaiveModel
                best_model = NaiveModel()
            elif best_model_name == "Seasonal Naive":
                from app.models.forecasting_models import SeasonalNaiveModel
                seasonal_period = best_params.get("seasonal_period", 7)
                best_model = SeasonalNaiveModel(seasonal_period=seasonal_period)
            else:
                raise ValueError(f"Unknown model: {best_model_name}")
            
            # Perform backtesting with the best model
            backtester = Backtester([best_model])
            backtest_results = backtester.backtest_single_model(best_model, time_series, 
                                                               train_size=0.8, 
                                                               forecast_horizon=forecast_steps)
        else:
            # Create models
            models = create_default_models()
            
            # Perform backtesting
            backtester = Backtester(models)
            backtest_results = backtester.backtest_all_models(time_series, train_size=0.8, 
                                                             forecast_horizon=forecast_steps)
            
            # Select best model
            best_model_name, best_results = backtester.select_best_model(backtest_results)
            
            # Create the best model instance
            if best_model_name == "Linear Regression":
                from app.models.forecasting_models import LinearRegressionModel
                best_model = LinearRegressionModel()
            elif best_model_name == "Moving Average":
                from app.models.forecasting_models import MovingAverageModel
                best_model = MovingAverageModel(window=7)
            elif best_model_name == "Exponential Smoothing":
                from app.models.forecasting_models import ExponentialSmoothingModel
                best_model = ExponentialSmoothingModel(trend='add')
            elif best_model_name == "Naive":
                from app.models.forecasting_models import NaiveModel
                best_model = NaiveModel()
            elif best_model_name == "Seasonal Naive":
                from app.models.forecasting_models import SeasonalNaiveModel
                best_model = SeasonalNaiveModel(seasonal_period=7)
            else:
                raise ValueError(f"Unknown model: {best_model_name}")
            
            backtest_results = {'mae': best_results.get('mae', float('inf')), 'mape': best_results.get('mape', float('inf'))}
        
        # Fit the best model on all data and forecast
        best_model.fit(time_series)
        forecast = best_model.predict(forecast_steps)
        
        # Create plot
        plot_base64 = plot_forecast(time_series, forecast, f"Forecast using {best_model_name}")
        
        # Prepare historical data for the response
        historical_dates = time_series.index.tolist()
        historical_values = time_series.tolist()
        
        # Prepare response
        result = ForecastResult(
            model_name=best_model_name,
            forecast=forecast.tolist(),
            dates=forecast.index.tolist(),
            metrics={
                "mae": backtest_results.get("mae", float('inf')),
                "mape": backtest_results.get("mape", float('inf'))
            },
            plot=plot_base64
        )
        
        return result
        
    except Exception as e:
        logger.error(f"CSV upload forecasting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV upload forecasting failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)