# Whoop Data - Python Library Guide

A practical guide to using the `whoop-data` Python library to access your Whoop fitness data.

## Table of Contents
- [Getting Started](#getting-started)
- [Getting Comprehensive Cycle Data](#getting-comprehensive-cycle-data)
- [Getting Heart Rate Data](#getting-heart-rate-data)
- [Getting Sleep Data](#getting-sleep-data)
- [Working with the Data](#working-with-the-data)
- [Data Field Reference](#data-field-reference)

---

## Getting Started

```python
from whoop_data import WhoopClient, get_cycle_data, get_heart_rate_data, get_sleep_data, save_to_json

# Initialize the client with your Whoop credentials
client = WhoopClient(username="your_email@example.com", password="your_password")

# Or use environment variables
# Set WHOOP_USERNAME and WHOOP_PASSWORD
client = WhoopClient()
```

---

## Getting Comprehensive Cycle Data

The most efficient way to get all your metrics in one call - recovery, sleep, strain, and workouts.

### Basic Usage

```python
# Get the last 7 days (default)
cycles = get_cycle_data(client)

# Get a specific date range
cycles = get_cycle_data(client, start_date="2025-10-01", end_date="2025-10-07")
```

### What You Get

Each cycle contains:
- **Date** - The day this cycle represents
- **Recovery** - HRV, resting heart rate, recovery score
- **Sleep** - Sleep score, duration, stages, efficiency, respiratory rate
- **Strain** - Day strain, heart rate metrics, calories burned
- **Workouts** - All activities with strain, heart rate, duration

### Example: Accessing Cycle Data

```python
cycles = get_cycle_data(client, start_date="2025-10-01", end_date="2025-10-07")

for cycle in cycles:
    # Basic info
    print(f"Date: {cycle['date']}")
    print(f"Cycle ID: {cycle['cycle_id']}")
    
    # Recovery metrics
    recovery = cycle['recovery']
    print(f"Recovery Score: {recovery['score']}%")
    print(f"HRV: {recovery['hrv']} ms")
    print(f"Resting HR: {recovery['resting_hr']} bpm")
    
    # Sleep metrics
    for sleep in cycle['sleep']:
        hours = sleep['quality_duration'] / 3600000  # Convert ms to hours
        print(f"Sleep Score: {sleep['score']}%")
        print(f"Sleep Duration: {hours:.1f} hours")
        print(f"Sleep Efficiency: {sleep['sleep_efficiency']:.1f}%")
        print(f"Respiratory Rate: {sleep['respiratory_rate']:.1f} breaths/min")
    
    # Strain metrics
    strain = cycle['strain']
    print(f"Day Strain: {strain['day_strain']:.1f}")
    calories = strain['day_kilojoules'] / 4.184 if strain['day_kilojoules'] else 0
    print(f"Calories: {calories:.0f}")
    
    # Workouts
    for workout in cycle['workouts']:
        print(f"Workout Strain: {workout['strain']:.1f}")
        print(f"Sport ID: {workout['sport_id']}")
        print(f"Max HR: {workout['max_heart_rate']} bpm")
```

### Complete Data Structure

```python
{
    "date": "2025-10-02",
    "cycle_id": 123456789,
    "days": "['2025-10-02','2025-10-03')",
    "during": "['2025-10-01T22:00:00.000Z','2025-10-02T22:00:00.000Z')",
    "timezone_offset": "-04:00",
    
    "recovery": {
        "score": 77,              # Recovery score (0-100%)
        "hrv": 52,                # Heart Rate Variability in milliseconds
        "resting_hr": 59          # Resting heart rate in bpm
    },
    
    "sleep": [
        {
            "activity_id": "987654321-uuid",
            "score": 84,                      # Sleep score (0-100%)
            "quality_duration": 25200000,     # Actual sleep time (milliseconds)
            "time_in_bed": 28800000,          # Total time in bed (milliseconds)
            "sleep_efficiency": 87.5,         # Percentage
            "respiratory_rate": 14.2,         # Breaths per minute
            "disturbances": 8,                # Number of disturbances
            "latency": 360000,                # Time to fall asleep (milliseconds)
            
            # Sleep stages (all in milliseconds)
            "light_sleep_duration": 12600000,
            "slow_wave_sleep_duration": 7200000,  # Deep sleep
            "rem_sleep_duration": 5400000,
            "wake_duration": 3600000,
            
            # Sleep debt tracking (milliseconds)
            "sleep_need": 28800000,           # How much sleep you need
            "debt_pre": 3600000,              # Sleep debt before sleep
            "debt_post": 1800000,             # Sleep debt after sleep
            
            "during": "['2025-10-01T23:30:00.000Z','2025-10-02T07:30:00.000Z')",
            "timezone_offset": "-04:00"
        }
    ],
    
    "strain": {
        "day_strain": 13.2,               # Daily strain (0-21 scale)
        "day_avg_heart_rate": 75,         # Average HR for the day
        "day_max_heart_rate": 165,        # Max HR for the day
        "day_kilojoules": 8500,           # Energy expenditure (divide by 4.184 for calories)
        "intensity_score": 0.75
    },
    
    "workouts": [
        {
            "id": null,                       # Workout ID (may be null)
            "sport_id": 1,                    # Sport type (0=generic, 1=running, 43=swimming, etc.)
            "strain": 11.3,                   # Workout strain
            "avg_heart_rate": 141,
            "max_heart_rate": 170,
            "kilojoules": 2250,               # Energy (divide by 4.184 for calories)
            "distance_meter": 3200,           # Distance in meters (may be null)
            "altitude_gain_meter": 45,        # Altitude gain (may be null)
            "altitude_change_meter": 50,      # Total altitude change (may be null)
            "during": "['2025-10-02T10:00:00.000Z','2025-10-02T10:40:00.000Z')",
            "zone_duration": {                # Time in heart rate zones (milliseconds, may be null)
                "zone_zero_milli": 60000,
                "zone_one_milli": 300000,
                "zone_two_milli": 1200000,
                "zone_three_milli": 600000,
                "zone_four_milli": 240000,
                "zone_five_milli": 0
            }
        }
    ]
}
```

---

## Getting Heart Rate Data

Get your heart rate measurements at different time resolutions.

### Basic Usage

```python
# Get heart rate data for a date range (default: 10-minute intervals)
hr_data = get_heart_rate_data(client, start_date="2025-10-01", end_date="2025-10-01")

# Get high-resolution data (1-minute intervals)
hr_data = get_heart_rate_data(client, start_date="2025-10-01", end_date="2025-10-01", step=60)

# Get ultra-high resolution (6-second intervals) - ideal for workout analysis
hr_data = get_heart_rate_data(client, start_date="2025-10-01", end_date="2025-10-01", step=6)
```

### Resolution Options

- `step=600` (default): Every 10 minutes - efficient for long-term trends
- `step=60`: Every minute - good for daily tracking
- `step=6`: Every 6 seconds - perfect for detailed workout analysis

### Example: Working with Heart Rate Data

```python
hr_data = get_heart_rate_data(client, start_date="2025-10-01", end_date="2025-10-01", step=60)

print(f"Total data points: {len(hr_data)}")

# Analyze the data
heart_rates = [point['heart_rate'] for point in hr_data]
avg_hr = sum(heart_rates) / len(heart_rates)
max_hr = max(heart_rates)
min_hr = min(heart_rates)

print(f"Average HR: {avg_hr:.0f} bpm")
print(f"Max HR: {max_hr} bpm")
print(f"Min HR: {min_hr} bpm")

# Access individual data points
for point in hr_data[:5]:  # First 5 points
    print(f"{point['datetime']}: {point['heart_rate']} bpm")
```

### Data Structure

```python
[
    {
        "timestamp": 1727820000237,           # Unix timestamp in milliseconds
        "datetime": "2025-10-01T10:00:00.237Z",  # Human-readable ISO format
        "heart_rate": 59                      # Heart rate in bpm
    },
    {
        "timestamp": 1727820006237,
        "datetime": "2025-10-01T10:00:06.237Z",
        "heart_rate": 61
    }
]
```

---

## Getting Sleep Data

Get detailed sleep stages and metrics.

### Basic Usage

```python
# Get sleep data for the last 7 days (default)
sleep_data = get_sleep_data(client)

# Get sleep data for a specific date range
sleep_data = get_sleep_data(client, start_date="2025-10-01", end_date="2025-10-07")
```

### Example: Analyzing Sleep

```python
sleep_data = get_sleep_data(client, start_date="2025-10-01", end_date="2025-10-07")

for sleep_record in sleep_data:
    print(f"\nDate: {sleep_record['date']}")
    print(f"Cycle ID: {sleep_record['cycle_id']}")
    print(f"Activity ID: {sleep_record['activity_id']}")
    
    # Access the detailed sleep stage data
    stages = sleep_record['data']
    
    # Each stage has a time range and type
    for stage in stages:
        stage_type = stage['type']
        duration = stage['during']
        print(f"  {stage_type}: {duration}")
```

### Sleep Stage Types

- **LATENCY**: Time it took to fall asleep
- **LIGHT**: Light sleep (N1/N2 stages)
- **SWS**: Slow Wave Sleep (deep sleep, N3 stage)
- **REM**: Rapid Eye Movement sleep
- **WAKE**: Periods awake during the night
- **DISTURBANCES**: Brief interruptions

### Data Structure

```python
[
    {
        "date": "2025-10-02",
        "cycle_id": 123456789,
        "activity_id": "987654321-uuid",
        "data": [
            {
                "during": "['2025-10-01T23:31:16.310Z','2025-10-02T00:04:47.320Z')",
                "type": "LIGHT"
            },
            {
                "during": "['2025-10-02T00:04:47.320Z','2025-10-02T00:35:22.115Z')",
                "type": "SWS"
            },
            {
                "during": "['2025-10-02T00:35:22.115Z','2025-10-02T01:15:10.220Z')",
                "type": "REM"
            },
            {
                "during": "['2025-10-02T01:15:10.220Z','2025-10-02T01:18:05.330Z')",
                "type": "WAKE"
            }
        ]
    }
]
```

---

## Working with the Data

### Saving to JSON

```python
# Save any data to a JSON file
save_to_json(cycles, "my_cycles.json")
save_to_json(hr_data, "my_heart_rate.json")
save_to_json(sleep_data, "my_sleep.json")
```

### Converting Units

```python
# Milliseconds to hours
hours = milliseconds / 3600000

# Kilojoules to calories
calories = kilojoules / 4.184

# Meters to kilometers
kilometers = meters / 1000

# Example
sleep_hours = cycle['sleep'][0]['quality_duration'] / 3600000
calories_burned = cycle['strain']['day_kilojoules'] / 4.184
distance_km = workout['distance_meter'] / 1000 if workout['distance_meter'] else 0

print(f"Slept {sleep_hours:.1f} hours")
print(f"Burned {calories_burned:.0f} calories")
print(f"Ran {distance_km:.2f} km")
```

### Sport ID Mapping

The library includes a complete mapping of all 185+ sport types:

```python
from whoop_data import SPORT_IDS, get_sport_name

# Get sport name from ID
sport_name = get_sport_name(workout['sport_id'])
print(f"Activity: {sport_name}")

# Or access the dictionary directly
print(SPORT_IDS[33])  # "Swimming"

# Common sport IDs:
# -1: Activity
# 0: Running
# 1: Cycling
# 33: Swimming
# 44: Yoga
# 45: Weightlifting
# 48: Functional Fitness
# 63: Walking
# 89: Commuting
# 96: HIIT

# See whoop_data/constants.py for the complete list of 185+ sports
```

**Popular Categories:**
- **Traditional Sports**: Running, Cycling, Swimming, Basketball, Soccer, Tennis, Golf
- **Gym Activities**: Weightlifting, Functional Fitness, HIIT, Yoga, Pilates, Spinning
- **Recovery**: Meditation, Sauna, Ice Bath, Massage Therapy, Stretching, Foam Rolling
- **Daily Activities**: Commuting, Walking, Dog Walking, Cooking, Cleaning
- **Parenting**: Dedicated Parenting, Babywearing, Playing with Child, Nursing a Baby
- **Unique**: Gaming, Sex, Hot Dog Challenge, DJ, Public Speaking, Chess

For the complete mapping of all 185 sport types, see `whoop_data/constants.py` or use:
```python
from whoop_data import SPORT_IDS
print(SPORT_IDS)  # Complete dictionary
```

### Building a Sleep Hypnogram

```python
import matplotlib.pyplot as plt
from datetime import datetime

sleep_data = get_sleep_data(client, start_date="2025-10-01", end_date="2025-10-01")

for sleep_record in sleep_data:
    stages = sleep_record['data']
    
    # Map stage types to numeric values for plotting
    stage_values = {
        'WAKE': 4,
        'REM': 3,
        'LIGHT': 2,
        'SWS': 1,
        'LATENCY': 0,
        'DISTURBANCES': 4
    }
    
    times = []
    values = []
    
    for stage in stages:
        # Parse the time range
        during = stage['during'].strip("[]()").replace("'", "").split(',')
        start_time = datetime.fromisoformat(during[0].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(during[1].replace('Z', '+00:00'))
        
        times.extend([start_time, end_time])
        value = stage_values.get(stage['type'], 0)
        values.extend([value, value])
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=2)
    plt.yticks([0, 1, 2, 3, 4], ['Latency', 'Deep (SWS)', 'Light', 'REM', 'Awake'])
    plt.xlabel('Time')
    plt.ylabel('Sleep Stage')
    plt.title(f'Sleep Hypnogram - {sleep_record["date"]}')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'sleep_hypnogram_{sleep_record["date"]}.png')
```

### Analyzing Workout Performance

```python
cycles = get_cycle_data(client, start_date="2025-10-01", end_date="2025-10-31")

# Collect all running workouts
running_workouts = []
for cycle in cycles:
    for workout in cycle['workouts']:
        if workout['sport_id'] == 1:  # Running
            running_workouts.append({
                'date': cycle['date'],
                'strain': workout['strain'],
                'avg_hr': workout['avg_heart_rate'],
                'max_hr': workout['max_heart_rate'],
                'calories': workout['kilojoules'] / 4.184 if workout['kilojoules'] else 0,
                'distance_km': workout['distance_meter'] / 1000 if workout['distance_meter'] else 0
            })

# Calculate averages
if running_workouts:
    avg_strain = sum(w['strain'] for w in running_workouts) / len(running_workouts)
    avg_hr = sum(w['avg_hr'] for w in running_workouts) / len(running_workouts)
    total_distance = sum(w['distance_km'] for w in running_workouts)
    
    print(f"Running Summary ({len(running_workouts)} workouts):")
    print(f"  Average Strain: {avg_strain:.1f}")
    print(f"  Average HR: {avg_hr:.0f} bpm")
    print(f"  Total Distance: {total_distance:.1f} km")
```

---

## Data Field Reference

### Time Formats

All timestamps are in **milliseconds** unless specified otherwise:
- **Sleep duration**: milliseconds (divide by 3,600,000 for hours)
- **Workout duration**: Parse the `during` field which is a time range
- **Timestamps**: Unix milliseconds (e.g., 1727820000237)
- **Dates**: ISO 8601 format (e.g., "2025-10-02T10:30:00.000Z")

### Energy and Distance Units

- **Energy**: Kilojoules (kJ) - divide by 4.184 to convert to calories
- **Distance**: Meters - divide by 1,000 to convert to kilometers
- **Altitude**: Meters
- **Heart Rate**: Beats per minute (bpm)
- **Respiratory Rate**: Breaths per minute

### Understanding Strain

Whoop strain is measured on a scale of 0-21:
- **0-9**: Low strain
- **10-13**: Moderate strain
- **14-17**: High strain  
- **18-21**: All out

### Understanding Recovery Score

Recovery score is a percentage (0-100%):
- **67-100% (Green)**: Recovered, ready for strain
- **34-66% (Yellow)**: Adequate recovery
- **0-33% (Red)**: Not recovered, rest recommended

### Understanding Sleep Score

Sleep score is a percentage (0-100%):
- **90-100%**: Excellent sleep
- **70-89%**: Good sleep
- **60-69%**: Adequate sleep
- **0-59%**: Poor sleep

---

## Tips and Best Practices

### 1. Date Ranges
- Dates should be in `YYYY-MM-DD` format
- The library handles timezone conversion automatically
- Default is last 7 days if no dates specified

### 2. Performance
- Use `get_cycle_data()` for most use cases - it's the most efficient
- Use `step=600` for heart rate data unless you need high resolution
- Save data to JSON files to avoid repeated API calls

### 3. Error Handling

```python
try:
    cycles = get_cycle_data(client, start_date="2025-10-01", end_date="2025-10-07")
except Exception as e:
    print(f"Error fetching data: {e}")
```

### 4. Data Availability
- Some fields may be `null` if data wasn't captured
- GPS data (distance, altitude) is only available for manually tracked workouts
- Recovery scores are calculated once sleep is complete

### 5. Logging

```python
from whoop_data import set_debug_logging, set_info_logging, disable_logging

# Enable detailed logging for debugging
set_debug_logging()

# Normal logging (default)
set_info_logging()

# Disable all logging
disable_logging()
```

---

## Complete Example

```python
from whoop_data import (
    WhoopClient, 
    get_cycle_data, 
    get_heart_rate_data,
    save_to_json,
    set_info_logging
)

# Setup
set_info_logging()
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get last week's data
cycles = get_cycle_data(client)

# Analyze the week
total_strain = 0
total_sleep_hours = 0
avg_recovery = []

for cycle in cycles:
    # Strain
    total_strain += cycle['strain']['day_strain']
    
    # Sleep
    for sleep in cycle['sleep']:
        hours = sleep['quality_duration'] / 3600000
        total_sleep_hours += hours
    
    # Recovery
    if cycle['recovery']['score']:
        avg_recovery.append(cycle['recovery']['score'])

print("\n=== Weekly Summary ===")
print(f"Average Daily Strain: {total_strain / len(cycles):.1f}")
print(f"Average Sleep: {total_sleep_hours / len(cycles):.1f} hours/night")
print(f"Average Recovery: {sum(avg_recovery) / len(avg_recovery):.0f}%" if avg_recovery else "No recovery data")

# Save the data
save_to_json(cycles, "weekly_data.json")
print("\nData saved to weekly_data.json")
```

---

For more information and advanced usage, see:
- [README.md](README.md) - Installation and quick start
- [examples/](examples/) - More code examples
