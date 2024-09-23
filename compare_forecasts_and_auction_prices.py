from from_nico_utils.print_args_func import print_args
from utils.saving_results import save_results_as_csv_and_plots
from utils.match_auction_forecast import (
    match_auction_with_forecast,
    merge_forecast_and_auction_dataframes,
)
from utils.small_methods import (
    make_df_more_readable,
    compute_forecast_metrics,
)
from typing import Union
from pathlib import Path
import polars as pl 
import argparse
import os 



def compute_performance_score(
    forecast_df_path: Union[str, Path, pl.DataFrame],
    auction_dir: Union[str, Path, pl.DataFrame],
    save_dir: Union[str, Path] = os.getcwd(),
) -> None:
    """Calculate and display performance metrics based on auction and forecast data.

    This function reads forecast and auction data, computes price differences, and 
    generates performance metrics for the forecasts. It can also save the results to a specified directory.

    Args:
        forecast_df_path (Union[str, Path, pl.DataFrame]): The path to the forecast data file 
            or a DataFrame containing the forecast data.
        auction_dir (Union[str, Path, pl.DataFrame]): The path to the auction data directory 
            or a DataFrame containing the auction data.
        save_dir (Union[str, Path], optional): The directory where results will be saved. 
            Defaults to the current working directory.

    Returns:
        None
    """

    # First read all forecast and auction data
    forecast_auction_mathces = match_auction_with_forecast(forecast_df_or_path=forecast_df_path, auction_df_or_dir=auction_dir)
    
    # Match the forecast data with the auction data
    merged_forecast_auction_df = merge_forecast_and_auction_dataframes(forecast_auction_mathces)
    
    # Compute price differences
    merged_forecast_auction_df = merged_forecast_auction_df.with_columns([
        (pl.col("DK1_forecast_price") - pl.col("Auction_Price_DK1")).alias("Price_Diff_DK1"),
        (pl.col("DK2_forecast_price") - pl.col("Auction_Price_DK2")).alias("Price_Diff_DK2")
    ])
    
    # Save the resulting dataframe 
    if save_dir:
        merged_forecast_auction_df = make_df_more_readable(pl_data=merged_forecast_auction_df)
        save_results_as_csv_and_plots(merged_forecast_auction_df, save_dir)

    # Compute metrics and print those
    dk1_metrics, dk2_metrics = compute_forecast_metrics(pl_data=merged_forecast_auction_df)
    print(f"DK1 Metrics: \n{dk1_metrics}")
    print(f"DK2 Metrics: \n{dk2_metrics}")

    return merged_forecast_auction_df





# Run from CLI 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read the forecast data from the csv file")
    parser.add_argument("--forecast_df_path", type=str, default="IBForecastNoScenariosDK.csv", help="Path to the forecast data")
    parser.add_argument("--auction_dir", type=str, default=os.getcwd(), help="Path to the data directory")
    parser.add_argument("--save_dir", type=str, default=os.path.join(os.getcwd(), "results_dir"), help="Path to save the resulting csv file")
    args = parser.parse_args()

    # Edit the args
    args.forecast_df_path = os.path.realpath(args.forecast_df_path)
    args.auction_dir = os.path.realpath(args.auction_dir)
    args.save_dir = os.path.realpath(args.save_dir)

    # Print the input args 
    print_args(args=args, ljust_length=25, init_str="This is the arguments chosen when comparing forecasts with auction data")

    # Run the function
    compute_performance_score(**vars(args))
    