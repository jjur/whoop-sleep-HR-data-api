#!/usr/bin/env python3
"""
Script to generate a hypnograph from Whoop sleep data.
"""
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dotenv import load_dotenv
import numpy as np

# Import library components
from whoop_data import (
    WhoopClient, 
    get_sleep_data, 
    save_to_json
)

# Load environment variables from .env file
load_dotenv()

def main():
    """Process sleep data and create a hypnograph."""
    # Initialize client using environment variables
    client = WhoopClient()
    
    # Get data for last night
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Fetching sleep data from {start_date} to {end_date}")
    
    # Get sleep data
    sleep_data = get_sleep_data(
        client=client,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"Retrieved {len(sleep_data)} sleep records")
    
    if not sleep_data:
        print("No sleep data found for the specified date range")
        return 1
    
    # Use the most recent sleep record
    sleep_record = sleep_data[0]
    
    # Extract sleep phases from the data
    sleep_stages = sleep_record['data']
    
    # Create a dataframe for sleep stages
    stages_data = []
    
    # Map for sleep stage values in the hypnograph (y-axis)
    stage_map = {
        'WAKE': 4,    # AWAKE at top
        'REM': 3,     # REM second from top
        'LIGHT': 2,   # LIGHT third from top
        'SWS': 1      # SWS at bottom (deep sleep)
    }
    
    for stage in sleep_stages:
        # Skip LATENCY and DISTURBANCES as they're not sleep phases
        if stage['type'] in ['LATENCY', 'DISTURBANCES']:
            continue
            
        # Convert WAKE to AWAKE for display purposes
        display_type = 'AWAKE' if stage['type'] == 'WAKE' else stage['type']
        
        # Extract start and end times from the 'during' field
        during = stage['during']
        # Clean up the string and extract start/end times
        times = during.replace("['", "").replace("')", "").split("','")
        start_time = datetime.strptime(times[0], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime(times[1], "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Add to our dataset
        stages_data.append({
            'start_time': start_time,
            'end_time': end_time,
            'stage': display_type,
            'stage_value': stage_map.get(stage['type'], 0)  # Use 0 for unknown types
        })
    
    # Convert to DataFrame and sort by start time
    df = pd.DataFrame(stages_data)
    df = df.sort_values('start_time')
    
    # Create a hypnograph
    plt.figure(figsize=(12, 6))
    
    # Plot each sleep stage as a horizontal line from start to end
    for _, row in df.iterrows():
        plt.hlines(
            y=row['stage_value'],
            xmin=row['start_time'],
            xmax=row['end_time'],
            linewidth=8,
            color=get_stage_color(row['stage'])
        )
    
    # Set y-axis ticks and labels
    plt.yticks([1, 2, 3, 4], ['SWS', 'LIGHT', 'REM', 'AWAKE'])
    
    # Format the x-axis to show times nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    
    # Add labels and title
    plt.title('Sleep Hypnograph')
    plt.xlabel('Time')
    plt.ylabel('Sleep Stage')
    
    # Add a grid for better readability
    plt.grid(True, axis='x', alpha=0.3)
    
    # Rotate date labels to prevent overlapping
    plt.gcf().autofmt_xdate()
    
    # Set y-axis limits with some padding
    plt.ylim(0.5, 4.5)
    
    # Set x-axis limits to the start and end of sleep
    if not df.empty:
        sleep_start = df['start_time'].min()
        sleep_end = df['end_time'].max()
        plt.xlim(sleep_start, sleep_end)
    
    # Tight layout for better spacing
    plt.tight_layout()
    
    # Save the plot
    output_file = "sleep_hypnograph.png"
    plt.savefig(output_file)
    print(f"Hypnograph saved to {output_file}")
    
    # Calculate and display sleep statistics
    calculate_sleep_statistics(df)
    
    return 0

def get_stage_color(stage):
    """Return color for each sleep stage."""
    colors = {
        'AWAKE': 'red',
        'REM': 'green',
        'LIGHT': 'blue',
        'SWS': 'purple'
    }
    return colors.get(stage, 'gray')

def calculate_sleep_statistics(df):
    """Calculate and display sleep statistics."""
    print("\nSleep Statistics:")
    
    # Calculate duration for each stage
    stage_durations = {}
    total_duration = timedelta(0)
    
    for _, row in df.iterrows():
        duration = row['end_time'] - row['start_time']
        stage = row['stage']
        
        if stage not in stage_durations:
            stage_durations[stage] = duration
        else:
            stage_durations[stage] += duration
            
        total_duration += duration
    
    # Convert to hours and minutes for display
    print(f"Total sleep duration: {format_duration(total_duration)}")
    
    # Show each stage duration and percentage
    for stage in ['SWS', 'LIGHT', 'REM', 'AWAKE']:
        if stage in stage_durations:
            duration = stage_durations[stage]
            percentage = (duration / total_duration) * 100
            print(f"{stage}: {format_duration(duration)} ({percentage:.1f}%)")

def format_duration(td):
    """Format timedelta as hours and minutes."""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

if __name__ == "__main__":
    exit(main()) 