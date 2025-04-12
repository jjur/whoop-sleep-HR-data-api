"""
Data processing functions for Whoop data.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from whoop_data.client import WhoopClient


def format_date(date_str: str) -> str:
    """
    Format date string to ISO format expected by the API.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        str: Formatted date in ISO format
    """
    if not date_str:
        return None
        
    # Convert YYYY-MM-DD to ISO format with time
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{date_obj.strftime('%Y-%m-%dT%H:%M:%S.000')}Z"


def get_default_date_range() -> Tuple[str, str]:
    """
    Get default date range (last 7 days) if not specified.
    
    Returns:
        tuple: (start_date, end_date) in ISO format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    return (
        f"{start_date.strftime('%Y-%m-%dT%H:%M:%S.000')}Z",
        f"{end_date.strftime('%Y-%m-%dT%H:%M:%S.000')}Z"
    )


def get_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[str, str]:
    """
    Get formatted date range for API requests.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        tuple: (start_date, end_date) in ISO format
    """
    if start_date and end_date:
        start_iso = format_date(start_date)
        end_iso = format_date(end_date)
        # Adjust end time to end of day
        end_iso = end_iso.replace("00:00:00.000Z", "23:59:59.999Z")
    else:
        start_iso, end_iso = get_default_date_range()
    
    return start_iso, end_iso


def get_sleep_data(client: WhoopClient, 
                  start_date: Optional[str] = None, 
                  end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get sleep data for a date range.
    
    Example:
        >>> from whoop_data import WhoopClient, get_sleep_data
        >>> client = WhoopClient(username="your_email@example.com", password="your_password")
        >>> sleep_data = get_sleep_data(client, "2023-01-01", "2023-01-07")
    
    Args:
        client: WhoopClient instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        list: List of sleep data records
    """
    # Get formatted date range
    start_iso, end_iso = get_date_range(start_date, end_date)
    print(f"Fetching sleep data from {start_iso} to {end_iso}")
    
    # Get cycles for the date range
    cycles = client.get_cycles(start_time=start_iso, end_time=end_iso)
    
    # Extract sleep data
    sleep_data = []
    
    for cycle in cycles:
        cycle_id = cycle.get("id")
        
        # Get sleep vows for the cycle
        try:
            sleep_vow = client.get_sleep_vow(cycle_id=str(cycle_id))
            
            # Get sleep events
            for sleep_event in sleep_vow.get("sleeps", []):
                activity_id = sleep_event.get("id")
                
                if activity_id:
                    # Get detailed sleep event data
                    sleep_detail = client.get_sleep_event(activity_id=str(activity_id))
                    
                    # Add to results
                    if sleep_detail:
                        sleep_data.append({
                            "date": cycle.get("day"),
                            "cycle_id": cycle_id,
                            "activity_id": activity_id,
                            "data": sleep_detail
                        })
        except Exception as e:
            print(f"Error processing cycle {cycle_id}: {str(e)}")
            continue
            
    return sleep_data


def get_heart_rate_data(client: WhoopClient, 
                       start_date: Optional[str] = None, 
                       end_date: Optional[str] = None,
                       step: int = 600) -> List[Dict[str, Any]]:
    """
    Get heart rate data for a date range.
    
    Example:
        >>> from whoop_data import WhoopClient, get_heart_rate_data
        >>> client = WhoopClient(username="your_email@example.com", password="your_password")
        >>> hr_data = get_heart_rate_data(client, "2023-01-01", "2023-01-07", step=300)
    
    Args:
        client: WhoopClient instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        step: Time step in seconds (default 600 = 10 minutes)
        
    Returns:
        list: Processed heart rate data
    """
    # Get formatted date range
    start_iso, end_iso = get_date_range(start_date, end_date)
    print(f"Fetching heart rate data from {start_iso} to {end_iso}")
    
    # Get heart rate data from API
    hr_data = client.get_heart_rate(start=start_iso, end=end_iso, step=step)
    
    # Process data into a more usable format
    processed_data = []
    
    if hr_data and "values" in hr_data:
        timestamps = hr_data.get("times", [])
        values = hr_data.get("values", [])
        
        # Combine timestamps and values
        for i in range(len(timestamps)):
            if i < len(values):
                processed_data.append({
                    "timestamp": timestamps[i],
                    "heart_rate": values[i]
                })
    
    return processed_data


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2) 