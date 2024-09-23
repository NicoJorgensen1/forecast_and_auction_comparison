from utils.small_methods import check_unique_time_ptime_combinations
from typing import Union
from pathlib import Path
import polars as pl
import os


def read_forecast_df(
        forecast_path: Union[str, Path],
        assure_unique_time_ptime_combinations: bool = True
) -> pl.DataFrame:
    """Read forecast data from a CSV file and process it into a DataFrame.

    This function loads forecast data from the specified file path, cleans the data by removing 
    null values and invalid entries, and ensures that the time combinations are unique if specified. 
    The resulting DataFrame contains properly formatted datetime and price columns.

    Args:
        forecast_path (Union[str, Path]): The path to the CSV file containing forecast data.
        assure_unique_time_ptime_combinations (bool, optional): A flag to check for unique 
            combinations of 'Time' and 'PTime'. Defaults to True.

    Raises:
        ValueError: If the forecast_path is None or if the combinations of 'Time' and 'PTime' 
            are not unique.
        FileNotFoundError: If the specified forecast_path does not exist.

    Returns:
        pl.DataFrame: A DataFrame containing the cleaned and processed forecast data.
    """

    if forecast_path is None:
        raise ValueError("forecast_path is None")
    if not os.path.isfile(forecast_path):
        raise FileNotFoundError(f"forecast_path: {forecast_path} does not exist")
    
    # Read the forecast data
    forecast_df = pl.read_csv(forecast_path)
    forecast_df = forecast_df.drop_nulls()
    forecast_df = forecast_df.filter(~pl.any_horizontal(forecast_df.select(pl.col("*") == "NA")))
    forecast_df = forecast_df.rename({"cor_pe_RegPrice.DK1": "DK1_forecast_price", "cor_pe_RegPrice.DK2": "DK2_forecast_price"})
    forecast_df = forecast_df.with_columns([
        pl.col("PTime").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S"),
        pl.col("Time").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S"),
        pl.col("DK1_forecast_price").cast(pl.Float64),
        pl.col("DK2_forecast_price").cast(pl.Float64)
    ])
    forecast_df = forecast_df.sort("PTime", descending=False)

    # Check if the combinations of "Time" and "PTime" are unique
    if assure_unique_time_ptime_combinations:
        are_combinations_unique = check_unique_time_ptime_combinations(forecast_df)
        if not are_combinations_unique:
            raise ValueError("The combinations of 'Time' and 'PTime' are not unique")
    
    return forecast_df