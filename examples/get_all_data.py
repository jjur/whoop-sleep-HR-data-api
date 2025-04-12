#!/usr/bin/env python3
"""
Example script showing how to use the whoop-data library to fetch both sleep and heart rate data.
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import library components
from whoop_data import WhoopClient, get_sleep_data, get_heart_rate_data, save_to_json

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to demonstrate library usage."""
    # Get credentials from .env file or environment variables
    username = os.getenv("WHOOP_USERNAME")
    password = os.getenv("WHOOP_PASSWORD")
    
    if not username or not password:
        print("Please set WHOOP_USERNAME and WHOOP_PASSWORD environment variables.")
        return 1
    
    # Initialize client with authentication
    client = WhoopClient(username=username, password=password)
    
    # Define date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Fetching data from {start_date} to {end_date}")
    
    # Get sleep data
    print("\n=== Sleep Data ===")
    sleep_data = get_sleep_data(
        client=client,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"Retrieved {len(sleep_data)} sleep records")
    
    # Save sleep data to file
    if sleep_data:
        output_file = "sleep_data.json"
        save_to_json(sleep_data, output_file)
        print(f"Sleep data saved to {output_file}")
    
    # Get heart rate data with 5-minute intervals
    print("\n=== Heart Rate Data ===")
    hr_data = get_heart_rate_data(
        client=client,
        start_date=start_date,
        end_date=end_date,
        step=300  # 5 minutes
    )
    
    print(f"Retrieved {len(hr_data)} heart rate records")
    
    # Save heart rate data to file
    if hr_data:
        output_file = "heart_rate_data.json"
        save_to_json(hr_data, output_file)
        print(f"Heart rate data saved to {output_file}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 