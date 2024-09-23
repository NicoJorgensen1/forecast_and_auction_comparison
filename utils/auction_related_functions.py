from from_nico_utils.recursive_search import search_files
from from_nico_utils.regex_find_pattern import datetime_from_string
from typing import Union
from pathlib import Path
from datetime import datetime
import polars as pl


def read_auction_files(
    aution_data_dir: Union[str, Path]
) -> pl.DataFrame:
    """Read auction result files from a specified directory and organize the data.

    This function scans the given directory for auction result files, extracts relevant 
    information such as region, IDA group, and dates, and returns a structured DataFrame 
    containing this data.

    Args:
        aution_data_dir (Union[str, Path]): The directory path containing auction result files.

    Returns:
        pl.DataFrame: A DataFrame with columns for file paths, region, IDA group, 
        written date, and delivery date.
    """

    # Read filepaths for all auction results -> auction_result_files is a recursive glob for all files with the matching extensions
    auction_result_files = search_files(aution_data_dir, accepted_img_extensions=(".csv", "xlsx"))
    auction_results_df = pl.DataFrame({
        "filepath": auction_result_files
    })
    
    # Map the files into the region and IDA group
    auction_results_df = auction_results_df.with_columns(
        pl.col("filepath").map_elements(lambda x: "DK1" if "DK1" in x else "DK2", return_dtype=pl.String).alias("Region")
    )
    auction_results_df = auction_results_df.with_columns(
        pl.col("filepath").map_elements(
            lambda x: "IDA1" if "IDA1" in x else "IDA2" if "IDA2" in x else "IDA3", return_dtype=pl.String,
        ).alias("IDA Group")
    )

    # Extract the datetime values from the filepaths -> this auction_date is None/Null for all rows ... 
    auction_results_df = auction_results_df.with_columns(
        pl.col("filepath").map_elements(lambda x: datetime_from_string(x)[0], return_dtype=pl.Datetime).dt.date()
        .alias("filepath_written_date")
    )
    # The relevant delivery_date is +1 day for IDA1 and IDA2, not for any other IDA group. Add timedelta(1) for IDA1 and IDA2 and name that new column delivery_date
    auction_results_df = auction_results_df.with_columns(
        pl.when(pl.col("IDA Group").is_in(["IDA1", "IDA2"]))
        .then(pl.col("filepath_written_date") + pl.duration(days=1))
        .otherwise(pl.col("filepath_written_date")).dt.date()
        .alias("delivery_date")
    )
    auction_results_df = auction_results_df.drop_nulls()
    auction_results_df = auction_results_df.sort("delivery_date", descending=False)
    return auction_results_df



def read_single_auction_file(auction_filepath: Union[str, Path], IDA_group: str, date: datetime, region: str) -> pl.DataFrame:
    """Read and process a single auction file to compute hourly average prices.

    This function reads auction data from a specified file, processes it to calculate 
    hourly average prices based on 15-minute intervals, and returns a DataFrame with 
    the computed averages for the specified region.

    Args:
        auction_filepath (Union[str, Path]): The path to the auction data file.
        IDA_group (str): The IDA group associated with the auction data.
        date (datetime): The date for which the auction data is relevant.
        region (str): The region associated with the auction data.

    Returns:
        pl.DataFrame: A DataFrame containing the hourly average auction prices for the specified region.
    """

    # Read the auction data
    auction_df = pl.read_excel(auction_filepath)
    auction_df = auction_df.drop_nulls()
    auction_df = auction_df.drop([col for col in auction_df.columns if "unnamed" in col.lower()])
    auction_df = auction_df.rename({"Type": "Quater_Time", "Schedule": "Area_Price"})

    # Convert the quater time into a datetime object
    start_hour, start_minute = 0 if IDA_group != "IDA3" else 12, 0
    auction_df = auction_df.with_columns(
        (pl.datetime(date.year, date.month, date.day, start_hour, start_minute, 0) + 
        pl.arange(0, auction_df.height) * pl.duration(minutes=15)).alias("Start_Time")
    )

    ### As the auction data is given in 15min intervals, we will compute the hourly average
    auction_df = auction_df.with_columns(pl.col("Area_Price").cast(pl.Float64))
    
    # Extract the date and hour from the 'Start_Time' column to use for grouping
    auction_df = auction_df.with_columns([
        pl.col("Start_Time").dt.date().alias("Date"),       # Extract date
        pl.col("Start_Time").dt.hour().alias("Hour")        # Extract hour
    ])


    # Group by 'Date' and 'Hour' and compute the hourly average
    hourly_averages_df = auction_df.group_by(["Date", "Hour"]).agg([
        pl.col("Area_Price").mean().alias("Area_Price_Hour"),  # Compute average for each hour
        pl.col("Start_Time").min().alias("Start_Time")         # Use the first (min) Start_Time for each hour
    ])
    hourly_averages_df = hourly_averages_df.sort("Start_Time", descending=False).drop(["Hour", "Date"])
    return hourly_averages_df.rename({"Area_Price_Hour": f"Auction_Price_{region}"})

