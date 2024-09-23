from utils.plotting_functions import (
    plot_price_diff_dist,
    plot_prices_and_diffs,
)
from typing import Union
from pathlib import Path
import polars as pl
import os


def save_results_as_csv_and_plots(
    merged_forecast_auction_df: pl.DataFrame,
    save_dir: Union[str, Path] = os.getcwd(),
) -> None:
    """Save the merged forecast and auction DataFrame as a CSV and generate associated plots.

    This function creates a directory if it does not exist, saves the provided DataFrame 
    as a CSV file, and generates visualizations of price differences and prices, saving 
    the plots to the specified directory.

    Args:
        merged_forecast_auction_df (pl.DataFrame): The DataFrame containing merged forecast 
            and auction data to be saved.
        save_dir (Union[str, Path], optional): The directory where the results will be saved. 
            Defaults to the current working directory.

    Returns:
        None
    """

    os.makedirs(save_dir, exist_ok=True)
    
    # Save the dataframe as a csv file
    csv_save_path = os.path.join(save_dir, "forecast_auction_performance.csv")
    merged_forecast_auction_df.write_csv(csv_save_path)

    # Visualize the distribution of price differences 
    plot_save_path = os.path.join(save_dir, "price_diff_dist.png")
    plot_price_diff_dist(pl_data=merged_forecast_auction_df, save_path=plot_save_path)

    # Visualize the prices and price differences
    plot_prices_save_path = os.path.join(save_dir, "prices_and_diffs.png")
    plot_prices_and_diffs(pl_data=merged_forecast_auction_df, save_path=plot_prices_save_path)

    return None