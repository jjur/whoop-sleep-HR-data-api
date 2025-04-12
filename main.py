#!/usr/bin/env python3
"""
Command-line tool for extracting sleep and heart rate data from Whoop.

Example usage:
    python main.py --username your_email@example.com --password your_password --data-type sleep --from-date 2023-01-01 --to-date 2023-01-07
"""
import argparse
import os
from datetime import datetime

from whoop_data import WhoopClient, get_sleep_data, get_heart_rate_data, save_to_json


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Extract sleep and heart rate data from Whoop")
    parser.add_argument("--username", "-u", help="Whoop account username/email")
    parser.add_argument("--password", "-p", help="Whoop account password")
    parser.add_argument("--from-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--data-type", "-t", choices=["sleep", "heart_rate", "all"], 
                        default="all", help="Type of data to extract")
    parser.add_argument("--step", type=int, default=600, 
                        help="Time step for heart rate data in seconds (default: 600)")
    
    return parser.parse_args()


def main():
    """Main entry point for the command-line tool."""
    args = parse_args()
    
    # Initialize client with authentication
    client = WhoopClient(username=args.username, password=args.password)
    
    # Create output directory if needed
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Current timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extract requested data
    if args.data_type in ["sleep", "all"]:
        sleep_results = get_sleep_data(
            client=client,
            start_date=args.from_date,
            end_date=args.to_date
        )
        print(f"Retrieved {len(sleep_results)} sleep records")
        
        # Save sleep data
        if sleep_results:
            output_file = args.output or f"{output_dir}/sleep_data_{timestamp}.json"
            save_to_json(sleep_results, output_file)
            print(f"Sleep data saved to {output_file}")
        
    if args.data_type in ["heart_rate", "all"]:
        hr_results = get_heart_rate_data(
            client=client,
            start_date=args.from_date,
            end_date=args.to_date,
            step=args.step
        )
        print(f"Retrieved {len(hr_results)} heart rate records")
        
        # Save heart rate data
        if hr_results:
            output_file = args.output or f"{output_dir}/heart_rate_data_{timestamp}.json"
            save_to_json(hr_results, output_file)
            print(f"Heart rate data saved to {output_file}")


if __name__ == "__main__":
    main() 