from utils.read_forecast_data import read_forecast_df
from utils.auction_related_functions import read_auction_files, read_single_auction_file
from datetime import timedelta
from typing import Union, List
from pathlib import Path
from tqdm import tqdm
import polars as pl


def merge_forecast_and_auction_dataframes(
        forecast_auction_mathces: List[pl.DataFrame]
) -> pl.DataFrame:
    """Merge multiple forecast and auction DataFrames into a single DataFrame.

    This function takes a list of DataFrames containing forecast and auction matches, 
    concatenates them, and filters the results to create a comprehensive DataFrame 
    that includes relevant auction prices while removing any rows with all null auction values.

    Args:
        forecast_auction_mathces (List[pl.DataFrame]): A list of DataFrames to be merged.

    Returns:
        pl.DataFrame: A single DataFrame containing the merged forecast and auction data.
    """

    # Merge all the forecast-auction matches into a single, large dataframe
    tmp_df, merged_forecast_auction_df = pl.DataFrame(), pl.DataFrame()
    for df in tqdm(forecast_auction_mathces):
        tmp_df = pl.concat([tmp_df, df], how="diagonal")
    time_filtering_prog_bar = tqdm(enumerate(tmp_df["Time"].unique()), leave=True, total=tmp_df["Time"].n_unique())
    tmp_df = tmp_df.sort("Time", descending=False)
    for time_idx, time in time_filtering_prog_bar:
        time_filtering_prog_bar.set_description(f"Filtering time {time_idx+1}/{len(time_filtering_prog_bar)}")
        time_df = tmp_df.filter(pl.col("Time") == pl.lit(time))
        for col in [col for col in time_df.columns if "price" in col.lower() and "forecast" not in col.lower()]:
            vals = time_df[col].to_list()
            vals_no_nulls = [val for val in vals if val is not None]
            vals_no_nulls += [None] * (len(vals) - len(vals_no_nulls))
            time_df = time_df.with_columns(pl.Series(col, vals_no_nulls))
        merged_forecast_auction_df = pl.concat([merged_forecast_auction_df, time_df])
    
    # Remove any rows where all auction values are None 
    merged_forecast_auction_df = merged_forecast_auction_df.filter(
        ~(pl.col("Auction_Price_DK1").is_null() & pl.col("Auction_Price_DK2").is_null())
    )
    merged_forecast_auction_df = merged_forecast_auction_df.sort("Time", descending=False)
    return merged_forecast_auction_df


def match_auction_with_forecast(
    forecast_df_or_path: Union[str, Path, pl.DataFrame],
    auction_df_or_dir: Union[str, Path, pl.DataFrame]
) -> None:
    """Match auction data with corresponding forecast data.

    This function reads auction and forecast data from specified sources, filters the auction 
    data to include only those with corresponding forecasts, and merges the relevant data 
    into a list of DataFrames for further analysis.

    Args:
        forecast_df_or_path (Union[str, Path, pl.DataFrame]): The path to the forecast data file 
            or a DataFrame containing the forecast data.
        auction_df_or_dir (Union[str, Path, pl.DataFrame]): The path to the auction data directory 
            or a DataFrame containing the auction data.

    Raises:
        ValueError: If no forecasts or relevant forecasts are found for an auction.
    """

    # Read the data
    forecast_df = read_forecast_df(forecast_path=forecast_df_or_path) if isinstance(forecast_df_or_path, str) else forecast_df_or_path
    all_auctions_df = read_auction_files(aution_data_dir=auction_df_or_dir) if isinstance(auction_df_or_dir, str) else auction_df_or_dir
    
    # Remove auction data that does not have a corresponding forecast
    all_auctions_df = all_auctions_df.filter(pl.col("delivery_date").is_in(forecast_df["Time"].dt.date()))
    all_auctions_df = all_auctions_df.sort(["delivery_date", "Region", "IDA Group"], descending=False)

    # Loop through each auction file 
    forecast_auction_mathces = []
    auction_row_dicts = all_auctions_df.to_dicts()
    dict_prog_bar = tqdm(enumerate(auction_row_dicts), total=len(auction_row_dicts), desc="Reading auction files", leave=True)
    for auction_idx, auction_dict in dict_prog_bar:
        ida_group = auction_dict.get("IDA Group")
        delivery_date = auction_dict.get("delivery_date")
        region = auction_dict.get("Region")
        dict_prog_bar.set_description(f"Reading auction file {auction_idx+1}/{len(auction_row_dicts)}. IDA Group: {ida_group}, Region: {region}, Delivery Date: {delivery_date.strftime('%d-%b-%Y')}")
        
        # Read the auction data
        auction_df = read_single_auction_file(auction_filepath=auction_dict.get("filepath"), IDA_group=ida_group, date=delivery_date, region=region)
        auction_start_time = auction_df["Start_Time"].min()
        auction_end_time = auction_df["Start_Time"].max()
        day_before_delivery = delivery_date - timedelta(days=1)  # Get the day before the delivery date

        # Read the corresponding forecast data for the auction
        ptime_hour_needed = 15 if ida_group == "IDA1" else (22 if ida_group == "IDA2" else 10)
        forecasts_for_auction = forecast_df.filter(
            (pl.col("PTime").dt.date() == pl.lit(delivery_date)) | 
            (pl.col("PTime").dt.date() == pl.lit(day_before_delivery))
        ).filter((pl.col("PTime").dt.hour() == ptime_hour_needed))
        forecasts_for_auction = forecasts_for_auction.sort("Time", descending=False)
        
        # Empty forecasts will only happen on occasions, where there are actually no forecasts in the forecast data
        if forecasts_for_auction.height == 0:
            raise ValueError(f"No forecasts found for auction: {auction_dict}!")

        # As the auction data last for either 12 or 24 hours, we will only consider the forecast data for the same time period
        relevant_forecasts = forecasts_for_auction.filter(
            (pl.col("Time") >= auction_start_time) & (pl.col("Time") <= auction_end_time)
        )
        if relevant_forecasts.height == 0:
            raise ValueError(f"No relevant forecasts found for auction: {auction_dict}!")
        auction_df_relevant = auction_df.filter(
            (pl.col("Start_Time") >= relevant_forecasts["Time"].min()) & 
            (pl.col("Start_Time") <= relevant_forecasts["Time"].max())
        )

        ### Now, we need to merge this data together
        joined_df = relevant_forecasts.join(
            auction_df_relevant, 
            left_on="Time", 
            right_on="Start_Time", 
            how="left"  # Use left join to retain all rows from relevant_forecasts
        )
        joined_df = joined_df.with_columns([
            pl.lit(ida_group).alias("IDA Group"),
            pl.lit(region).alias("Region"),
            pl.lit(auction_dict.get("filepath")).alias("Auction_Filepath"),
        ])
        forecast_auction_mathces.append(joined_df)
    return forecast_auction_mathces