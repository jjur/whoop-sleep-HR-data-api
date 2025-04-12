#!/usr/bin/env python3
"""
Example script showing how to process Whoop data for analysis.
"""
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib.dates import DateFormatter

# Import library components
from whoop_data import WhoopClient, get_heart_rate_data

# Load environment variables from .env file
load_dotenv()

def main():
    """Process heart rate data and create a visualization."""
    # Initialize client using environment variables
    client = WhoopClient()
    
    # Get data for the last 7 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Fetching heart rate data from {start_date} to {end_date}")
    
    # Get heart rate data
    hr_data = get_heart_rate_data(
        client=client,
        start_date=start_date,
        end_date=end_date,
        step=60  # 1-minute intervals
    )
    
    print(f"Retrieved {len(hr_data)} heart rate data points")
    
    # Convert to pandas DataFrame for easier analysis
    df = pd.DataFrame(hr_data)
    
    # Convert datetime string to proper datetime objects
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Set datetime as index
    df.set_index('datetime', inplace=True)
    
    # Make sure heart_rate is numeric
    df['heart_rate'] = pd.to_numeric(df['heart_rate'])
    
    # Create a plot showing all data points
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['heart_rate'], '-')
    plt.title('Heart Rate Data (All Points)')
    plt.ylabel('Heart Rate (bpm)')
    
    # Format the date/time on x-axis to be more readable
    date_format = DateFormatter('%m-%d %H:%M')  # Month-Day Hour:Minute
    plt.gca().xaxis.set_major_formatter(date_format)
    
    # Rotate date labels to prevent overlapping
    plt.gcf().autofmt_xdate()
    
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    output_file = "heart_rate_plot.png"
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    
    # Display some statistics
    print("\nHeart Rate Statistics:")
    print(f"Average: {df['heart_rate'].mean():.1f} bpm")
    print(f"Maximum: {df['heart_rate'].max()} bpm")
    print(f"Minimum: {df['heart_rate'].min()} bpm")
    
    return 0

if __name__ == "__main__":
    exit(main()) 