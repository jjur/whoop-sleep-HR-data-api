"""
Data processing functions for Whoop data.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from whoop_data.client import WhoopClient
from whoop_data.logger import get_logger

# Get logger instance
logger = get_logger()


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
    
    logger.debug(f"Formatting date string: {date_str}")
    # Convert YYYY-MM-DD to ISO format with time
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted = f"{date_obj.strftime('%Y-%m-%dT%H:%M:%S.000')}Z"
    logger.debug(f"Formatted date: {formatted}")
    return formatted


def get_default_date_range() -> Tuple[str, str]:
    """
    Get default date range (last 7 days) if not specified.
    
    Returns:
        tuple: (start_date, end_date) in ISO format
    """
    logger.debug("Calculating default date range (last 7 days)")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    start_iso = f"{start_date.strftime('%Y-%m-%dT%H:%M:%S.000')}Z"
    end_iso = f"{end_date.strftime('%Y-%m-%dT%H:%M:%S.000')}Z"
    
    logger.debug(f"Default date range: {start_iso} to {end_iso}")
    return (start_iso, end_iso)


def get_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[str, str]:
    """
    Get formatted date range for API requests.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        tuple: (start_date, end_date) in ISO format
    """
    logger.debug(f"Processing date range: start={start_date}, end={end_date}")
    
    if start_date and end_date:
        logger.debug("Using provided date range")
        start_iso = format_date(start_date)
        end_iso = format_date(end_date)
        # Adjust end time to end of day
        end_iso = end_iso.replace("00:00:00.000Z", "23:59:59.999Z")
        logger.debug(f"Adjusted end time to end of day: {end_iso}")
    else:
        logger.debug("Using default date range")
        start_iso, end_iso = get_default_date_range()
    
    return start_iso, end_iso


def get_cycle_data(client: WhoopClient,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get comprehensive cycle data including recovery, sleep, strain, and activity metrics.
    
    This function exposes all the rich data from the cycles BFF endpoint including:
    - Recovery metrics (HRV, resting HR, recovery score)
    - Sleep metrics (score, quality, duration, efficiency, respiratory rate, sleep need)
    - Strain metrics (day strain, max HR, average HR, calories)
    - Activity details (workouts with types, duration, strain)
    
    Example:
        >>> from whoop_data import WhoopClient, get_cycle_data
        >>> client = WhoopClient(username="your_email@example.com", password="your_password")
        >>> cycles = get_cycle_data(client, "2023-01-01", "2023-01-07")
        >>> for cycle in cycles:
        ...     print(f"Date: {cycle['date']}")
        ...     print(f"Recovery: {cycle['recovery']['score']}%")
        ...     print(f"HRV: {cycle['recovery']['hrv']}")
        ...     print(f"Sleep Score: {cycle['sleep']['score']}%")
        ...     print(f"Day Strain: {cycle['strain']['day_strain']}")
    
    Args:
        client: WhoopClient instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        list: List of cycle records with comprehensive metrics
    """
    logger.info(f"Getting comprehensive cycle data for date range: start={start_date}, end={end_date}")
    
    # Get formatted date range
    start_iso, end_iso = get_date_range(start_date, end_date)
    logger.info(f"Fetching cycle data from {start_iso} to {end_iso}")
    
    # Get cycles for the date range
    cycles_response = client.get_cycles(start_time=start_iso, end_time=end_iso)
    
    # Extract the actual cycle records from the response
    if isinstance(cycles_response, dict) and 'records' in cycles_response:
        cycles = cycles_response.get('records', [])
    else:
        cycles = cycles_response
        
    logger.info(f"Retrieved {len(cycles)} cycles")
    
    # Process and structure the data
    cycle_data = []
    
    for cycle_record in cycles:
        if not isinstance(cycle_record, dict) or 'cycle' not in cycle_record:
            continue
            
        cycle = cycle_record.get('cycle', {})
        sleeps = cycle_record.get('sleeps', [])
        
        # Parse the date range from the 'days' field
        days = cycle.get('days', '')
        date = days.replace("['", "").replace("')", "").split("','")[0] if days else ""
        
        # Extract recovery metrics
        recovery_data = {
            'score': cycle_record.get('score'),  # Recovery score
            'hrv': cycle_record.get('hrv_rmssd_milli'),  # HRV in milliseconds
            'resting_hr': cycle_record.get('resting_heart_rate'),  # Resting heart rate
        }
        
        # Extract sleep metrics from sleep events
        sleep_metrics = []
        for sleep_event in sleeps:
            sleep_metrics.append({
                'activity_id': sleep_event.get('activity_id'),
                'score': sleep_event.get('score'),
                'quality_duration': sleep_event.get('quality_duration'),  # milliseconds
                'latency': sleep_event.get('latency'),  # milliseconds
                'disturbances': sleep_event.get('disturbances'),
                'time_in_bed': sleep_event.get('time_in_bed'),  # milliseconds
                'light_sleep_duration': sleep_event.get('light_sleep_duration'),  # milliseconds
                'slow_wave_sleep_duration': sleep_event.get('slow_wave_sleep_duration'),  # milliseconds
                'rem_sleep_duration': sleep_event.get('rem_sleep_duration'),  # milliseconds
                'wake_duration': sleep_event.get('wake_duration'),  # milliseconds
                'sleep_efficiency': sleep_event.get('sleep_efficiency'),  # percentage
                'respiratory_rate': sleep_event.get('respiratory_rate'),  # breaths per minute
                'sleep_need': sleep_event.get('sleep_need'),  # milliseconds
                'debt_pre': sleep_event.get('debt_pre'),  # milliseconds
                'debt_post': sleep_event.get('debt_post'),  # milliseconds
                'during': sleep_event.get('during'),
                'timezone_offset': sleep_event.get('timezone_offset'),
            })
        
        # Extract strain metrics
        strain_data = {
            'day_strain': cycle.get('scaled_strain'),
            'day_avg_heart_rate': cycle.get('day_avg_heart_rate'),
            'day_max_heart_rate': cycle.get('day_max_heart_rate'),
            'day_kilojoules': cycle.get('day_kilojoules'),
            'intensity_score': cycle.get('intensity_score'),
        }
        
        # Extract activity/workout data
        workouts = cycle_record.get('workouts', [])
        activity_data = []
        for workout in workouts:
            activity_data.append({
                'id': workout.get('id'),
                'sport_id': workout.get('sport_id'),
                'during': workout.get('during'),
                'strain': workout.get('score'),
                'avg_heart_rate': workout.get('average_heart_rate'),
                'max_heart_rate': workout.get('max_heart_rate'),
                'kilojoules': workout.get('kilojoules'),
                'distance_meter': workout.get('distance_meter'),
                'altitude_gain_meter': workout.get('altitude_gain_meter'),
                'altitude_change_meter': workout.get('altitude_change_meter'),
                'zone_duration': workout.get('zone_duration'),  # Time in each HR zone
            })
        
        # Compile the comprehensive record
        cycle_data.append({
            'date': date,
            'cycle_id': cycle.get('id'),
            'days': days,
            'during': cycle.get('during'),
            'timezone_offset': cycle.get('timezone_offset'),
            'recovery': recovery_data,
            'sleep': sleep_metrics,
            'strain': strain_data,
            'workouts': activity_data,
        })
    
    logger.info(f"Successfully processed {len(cycle_data)} cycle records")
    return cycle_data


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
    logger.info(f"Getting sleep data for date range: start={start_date}, end={end_date}")
    
    # Get formatted date range
    start_iso, end_iso = get_date_range(start_date, end_date)
    logger.info(f"Fetching sleep data from {start_iso} to {end_iso}")
    
    # Get cycles for the date range
    logger.debug("Requesting cycle data")
    cycles_response = client.get_cycles(start_time=start_iso, end_time=end_iso)
    
    # Extract the actual cycle records from the response
    if isinstance(cycles_response, dict) and 'records' in cycles_response:
        cycles = cycles_response.get('records', [])
    else:
        cycles = cycles_response
        
    logger.info(f"Retrieved {len(cycles)} cycles")
    
    # Extract sleep data
    sleep_data = []
    
    for cycle_idx, cycle_record in enumerate(cycles):
        # Extract the cycle from the record
        if isinstance(cycle_record, dict) and 'cycle' in cycle_record:
            cycle = cycle_record.get('cycle', {})
            cycle_id = cycle.get("id")
            logger.debug(f"Processing cycle {cycle_idx+1}/{len(cycles)}: ID {cycle_id}")
            
            # Check if there are sleeps in the record
            sleep_events = cycle_record.get('sleeps', [])
            if sleep_events:
                logger.debug(f"Found {len(sleep_events)} sleep events in record")
                
                for event_idx, sleep_event in enumerate(sleep_events):
                    activity_id = sleep_event.get("activity_id")
                    
                    if activity_id:
                        logger.debug(f"Processing sleep event {event_idx+1}/{len(sleep_events)}: ID {activity_id}")
                        # Get detailed sleep event data
                        try:
                            sleep_detail = client.get_sleep_event(activity_id=str(activity_id))
                            
                            # Add to results
                            if sleep_detail:
                                sleep_data.append({
                                    "date": cycle.get("days", "").replace("['", "").replace("','", "").split(",")[0] if cycle.get("days") else "",
                                    "cycle_id": cycle_id,
                                    "activity_id": activity_id,
                                    "data": sleep_detail
                                })
                                logger.debug(f"Added sleep record for date: {cycle.get('days')}")
                        except Exception as e:
                            logger.error(f"Error getting sleep event {activity_id}: {str(e)}")
                    else:
                        logger.warning(f"Sleep event has no activity ID, skipping")
            else:
                # Try the old way to get sleep vow data
                try:
                    logger.debug(f"No sleeps found in record, trying sleep vow for cycle ID: {cycle_id}")
                    sleep_vow = client.get_sleep_vow(cycle_id=str(cycle_id))
                    
                    # Get sleep events
                    vow_sleep_events = sleep_vow.get("sleeps", [])
                    logger.debug(f"Found {len(vow_sleep_events)} sleep events from vow for cycle {cycle_id}")
                    
                    for event_idx, sleep_event in enumerate(vow_sleep_events):
                        activity_id = sleep_event.get("id")
                        
                        if activity_id:
                            logger.debug(f"Processing sleep event from vow {event_idx+1}/{len(vow_sleep_events)}: ID {activity_id}")
                            # Get detailed sleep event data
                            sleep_detail = client.get_sleep_event(activity_id=str(activity_id))
                            
                            # Add to results
                            if sleep_detail:
                                sleep_data.append({
                                    "date": cycle.get("days", "").replace("['", "").replace("','", "").split(",")[0] if cycle.get("days") else "",
                                    "cycle_id": cycle_id,
                                    "activity_id": activity_id,
                                    "data": sleep_detail
                                })
                                logger.debug(f"Added sleep record for date: {cycle.get('days')}")
                        else:
                            logger.warning(f"Sleep event from vow has no activity ID, skipping")
                except Exception as e:
                    logger.error(f"Error processing sleep vow for cycle {cycle_id}: {str(e)}")
                    continue
        else:
            logger.warning(f"Cycle record format not recognized: {cycle_record}")
    
    logger.info(f"Successfully retrieved {len(sleep_data)} sleep records")        
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
        >>> hr_data = get_heart_rate_data(client, "2023-01-01", "2023-01-07", step=60)
    
    Args:
        client: WhoopClient instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        step: Time step in seconds (only 6, 60, or 600 allowed, default 600 = 10 minutes)
        
    Returns:
        list: Processed heart rate data
    """
    logger.info(f"Getting heart rate data for date range: start={start_date}, end={end_date}, step={step}")
    
    # Validate step size - only specific values are allowed
    VALID_STEPS = [6, 60, 600]  # 6 seconds, 1 minute, or 10 minutes
    
    if step not in VALID_STEPS:
        # Find the closest valid step
        closest_step = min(VALID_STEPS, key=lambda x: abs(x - step))
        logger.warning(f"Step size {step} is not valid. Allowed values are {VALID_STEPS}. Using {closest_step} instead.")
        step = closest_step
    
    # Get formatted date range
    start_iso, end_iso = get_date_range(start_date, end_date)
    logger.info(f"Fetching heart rate data from {start_iso} to {end_iso}")
    
    # Get heart rate data from API
    logger.debug("Requesting heart rate data from API")
    hr_data = client.get_heart_rate(start=start_iso, end=end_iso, step=step)
    
    # Process data into a more usable format
    processed_data = []
    
    if hr_data and "values" in hr_data:
        values = hr_data.get("values", [])
        logger.debug(f"Processing {len(values)} heart rate values")
        
        # Process each heart rate data point
        for value in values:
            if "data" in value and "time" in value:
                # Convert Unix timestamp (milliseconds) to datetime string
                try:
                    timestamp_ms = value["time"]
                    # Convert milliseconds to seconds
                    timestamp_sec = timestamp_ms / 1000
                    # Convert to datetime object
                    dt = datetime.fromtimestamp(timestamp_sec)
                    # Format as ISO string
                    datetime_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    
                    processed_data.append({
                        "timestamp": timestamp_ms,  # Keep original for reference
                        "datetime": datetime_str,   # Add human-readable datetime
                        "heart_rate": value["data"]
                    })
                except Exception as e:
                    logger.warning(f"Error converting timestamp {value['time']}: {str(e)}")
                    # Fall back to just using the raw timestamp
                    processed_data.append({
                        "timestamp": value["time"],
                        "heart_rate": value["data"]
                    })
        
        logger.info(f"Successfully processed {len(processed_data)} heart rate data points")
    else:
        logger.warning(f"No heart rate data found in response: {hr_data}")
    
    return processed_data


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Output filename
    """
    logger.info(f"Saving data to {filename}")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved {len(data)} records to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")
        raise 