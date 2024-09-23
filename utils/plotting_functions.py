from matplotlib import pyplot as plt
from typing import Union
from pathlib import Path
import polars as pl
import os


def plot_price_diff_dist(
        pl_data: pl.DataFrame,
        save_path: Union[str, Path] = os.getcwd(),
) -> None:
    """Plot the distribution of price differences for DK1 and DK2.

    This function generates histograms for the price difference distributions of DK1 and DK2 
    from the provided DataFrame and saves the resulting plot to a specified location.

    Args:
        pl_data (pl.DataFrame): A DataFrame containing the price difference data for DK1 and DK2.
        save_path (Union[str, Path], optional): The path where the plot will be saved. 
            Defaults to the current working directory.

    Returns:
        None
    """

    fig = plt.figure(figsize=(12, 6))

    # Subplot for DK1
    plt.subplot(1, 2, 1)
    plt.hist(pl_data['Price_Diff_DK1'], bins=30, color='blue', edgecolor='black')
    plt.title('Price Difference Distribution for DK1')
    plt.grid(True)
    plt.xlabel('Price Difference (DK1)')
    plt.ylabel('Frequency')

    # Subplot for DK2
    plt.subplot(1, 2, 2)
    plt.hist(pl_data['Price_Diff_DK2'], bins=30, color='green', edgecolor='black')
    plt.title('Price Difference Distribution for DK2')
    plt.grid(True)
    plt.xlabel('Price Difference (DK2)')
    plt.ylabel('Frequency')

    # Adjust layout to prevent overlap
    fig.tight_layout()

    # Save the plot
    fig.savefig(fname=save_path, dpi=250, bbox_inches='tight') 
    return None


def plot_prices_and_diffs(
        pl_data: pl.DataFrame,
        save_path: Union[str, Path] = os.getcwd(),
) -> None:
    """Plot auction prices, forecasted prices, and price differences for DK1 and DK2.

    This function creates a visual representation of auction prices, forecasted prices, 
    and price differences for both DK1 and DK2, displaying them in two subplots. 
    The resulting figure is saved to a specified location.

    Args:
        pl_data (pl.DataFrame): A DataFrame containing time series data for auction prices, 
            forecasted prices, and price differences for DK1 and DK2.
        save_path (Union[str, Path], optional): The path where the plot will be saved. 
            Defaults to the current working directory.

    Returns:
        None
    """

    # Create a new figure with 2 subplots (one for DK1, one for DK2)
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Plot for DK1
    axes[0].plot(pl_data['Time'], pl_data['Auction_Price_DK1'], label='Auction Price DK1', color='blue')
    axes[0].plot(pl_data['Time'], pl_data['DK1_forecast_price'], label='Forecasted Price DK1', color='red', linestyle=None, marker=".", markeredgecolor='red', markerfacecolor="red")
    axes[0].bar(pl_data['Time'], pl_data['Price_Diff_DK1'], label='Price Difference DK1', color='black', alpha=0.5)

    axes[0].set_title('DK1: Auction Price, Forecasted Price, and Price Difference')
    axes[0].set_ylabel('Price')
    axes[0].set_xlim(pl_data['Time'].min(), pl_data['Time'].max())
    axes[0].grid(True)
    axes[0].legend()

    # Plot for DK2
    axes[1].plot(pl_data['Time'], pl_data['Auction_Price_DK2'], label='Auction Price DK2', color='blue')
    axes[1].plot(pl_data['Time'], pl_data['DK2_forecast_price'], label='Forecasted Price DK2', color='red', linestyle='-.')
    axes[1].bar(pl_data['Time'], pl_data['Price_Diff_DK2'], label='Price Difference DK2', color='black', alpha=0.5)

    axes[1].set_title('DK2: Auction Price, Forecasted Price, and Price Difference')
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('Price')
    axes[1].grid(True)
    axes[1].legend()

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)
    
    # Save the figure 
    fig.tight_layout()
    fig.savefig(fname=save_path, dpi=250, bbox_inches='tight')    
    return None
