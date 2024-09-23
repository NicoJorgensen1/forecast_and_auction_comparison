from typing import Tuple
import polars as pl


def check_unique_time_ptime_combinations(df: pl.DataFrame) -> bool:
    """
    Check if all combinations of "Time" and "PTime" in the DataFrame are unique.

    This function counts the unique combinations of the "Time" and "PTime" columns in the provided DataFrame
    and compares this count to the total number of rows. It returns True if all combinations are unique, 
    and False otherwise.

    Args:
        df (pl.DataFrame): The DataFrame containing "Time" and "PTime" columns to check for uniqueness.

    Returns:
        bool: True if all combinations of "Time" and "PTime" are unique, False otherwise.
    """
    # Count the number of unique combinations of "Time" and "PTime"
    unique_combinations_count = df.select([pl.col("Time"), pl.col("PTime")]).unique().height
    
    # Compare with the total number of rows in the DataFrame
    total_rows = df.height
    
    # Return True if all combinations are unique, False otherwise
    return unique_combinations_count == total_rows



def make_df_more_readable(
        pl_data: pl.DataFrame
) -> pl.DataFrame:
    """Reorganize the columns of a DataFrame for improved readability.

    This function rearranges the columns of the provided DataFrame by grouping them into 
    categories such as file paths, time, prices, and other columns. The resulting DataFrame 
    is structured to enhance clarity, especially when saved to a CSV file.

    Args:
        pl_data (pl.DataFrame): The DataFrame to be reorganized.

    Returns:
        pl.DataFrame: A new DataFrame with columns ordered for better readability.
    """

    # Order the columns of the dataframe - this is done only to make the resulting csv file more readable
    filepath_col = sorted([col for col in pl_data.columns if "filepath" in col.lower()], key=lambda x: x.lower())
    price_cols = sorted([col for col in pl_data.columns if "price" in col.lower()], key=lambda x: x.lower())
    time_cols = sorted([col for col in pl_data.columns if "time" in col.lower()], key=lambda x: x.lower())
    other_cols = sorted([col for col in pl_data.columns if col not in price_cols and col not in time_cols and col not in filepath_col], key=lambda x: x.lower())
    pl_data = pl_data.select(filepath_col + time_cols + price_cols + other_cols)
    return pl_data


def compute_forecast_metrics(
        pl_data: pl.DataFrame
) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Calculate forecast accuracy metrics for DK1 and DK2.

    This function computes various metrics including Mean Absolute Error (MAE), Mean Squared Error (MSE), 
    Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE) for the forecasted prices 
    of DK1 and DK2 compared to their respective auction prices. The results are returned as two separate 
    DataFrames for further analysis.

    Args:
        pl_data (pl.DataFrame): A DataFrame containing forecasted and auction prices for DK1 and DK2.

    Returns:
        Tuple[pl.DataFrame, pl.DataFrame]: Two DataFrames containing the computed metrics for DK1 and DK2.
    """

    epsilon = 1e-10  # Define a small epsilon to avoid division by zero

    # Calculate MAE, MSE, RMSE, and MAPE for DK1
    metrics_dk1 = pl_data.select([
        (pl.col("DK1_forecast_price") - pl.col("Auction_Price_DK1")).abs().mean().alias("MAE_DK1"),
        (pl.col("DK1_forecast_price") - pl.col("Auction_Price_DK1")).pow(2).mean().alias("MSE_DK1"),
        (pl.col("DK1_forecast_price") - pl.col("Auction_Price_DK1")).pow(2).mean().sqrt().alias("RMSE_DK1"),
        ((pl.col("DK1_forecast_price") - pl.col("Auction_Price_DK1")).abs() /
        pl.when(pl.col("Auction_Price_DK1") == 0).then(epsilon).otherwise(pl.col("Auction_Price_DK1"))
        ).mean().alias("MAPE_DK1")
    ])

    # Calculate metrics for DK2
    metrics_dk2 = pl_data.select([
        (pl.col("DK2_forecast_price") - pl.col("Auction_Price_DK2")).abs().mean().alias("MAE_DK2"),
        (pl.col("DK2_forecast_price") - pl.col("Auction_Price_DK2")).pow(2).mean().alias("MSE_DK2"),
        (pl.col("DK2_forecast_price") - pl.col("Auction_Price_DK2")).pow(2).mean().sqrt().alias("RMSE_DK2"),
        ((pl.col("DK2_forecast_price") - pl.col("Auction_Price_DK2")).abs() /
        pl.when(pl.col("Auction_Price_DK2") == 0).then(epsilon).otherwise(pl.col("Auction_Price_DK2"))
        ).mean().alias("MAPE_DK2")
    ])

    return metrics_dk1, metrics_dk2