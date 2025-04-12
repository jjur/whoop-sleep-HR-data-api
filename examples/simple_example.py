#!/usr/bin/env python3
"""
A minimal example showing how to use the whoop-data library with just a few lines of code.
"""
from whoop_data import WhoopClient, get_heart_rate_data, get_sleep_data, save_to_json

# Create a client (you can also use environment variables WHOOP_USERNAME and WHOOP_PASSWORD)
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get heart rate data for the default time range (last 7 days)
hr_data = get_heart_rate_data(client=client)
print(f"Retrieved {len(hr_data)} heart rate data points")
save_to_json(hr_data, "heart_rate.json")

# Get sleep data for the default time range (last 7 days)
sleep_data = get_sleep_data(client=client)
print(f"Retrieved {len(sleep_data)} sleep records")
save_to_json(sleep_data, "sleep.json") 