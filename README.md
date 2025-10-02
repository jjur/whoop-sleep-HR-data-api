# Whoop HeartRate and Sleep Python API

> Updated October 2025 to use new cycles API endpoint for sleep detection
> Updated July 2025 to use new login API endpoint

A simple Python library to access Whoop's internal web app API for extracting sleep and heart rate data.

> **Note**: This is an unofficial library based on reverse-engineered API endpoints and is not affiliated with or endorsed by Whoop. The API endpoints may change without notice.

## Features

- Authenticate with Whoop using your account credentials
- Extract data from app.whoop.com using internal API:
  - **Comprehensive Cycle Data** (NEW!) - Recovery, sleep, strain, and activities in one call
  - Sleep data including sleep stages, disturbances, and metrics
  - Heart rate data with customizable time intervals (6 seconds, 1 minute, or 10 minutes)
  - Activity/workout data including strain, heart rate zones, and performance metrics
  - Sports history - list of all sports/activities tracked


## Installation

```bash
# From PyPI
pip install whoop-data

# From source
git clone https://github.com/jjur/whoop-sleep-HR-data-api.git
cd whoop-sleep-HR-data-api
pip install -e .
```

## Quick Start

Retrieving data is as simple as:

```python
from whoop_data import WhoopClient, get_heart_rate_data

# Create a client (credentials can also be set via environment variables)
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get heart rate data (defaults to last 7 days if dates not specified)
hr_data = get_heart_rate_data(client=client)
```

You can also specify date ranges and customize the sampling interval:

```python
# Get heart rate data for a specific date range with 5-minute intervals
hr_data = get_heart_rate_data(
    client=client,
    start_date="2023-01-01",
    end_date="2023-01-07",
    step=60  # 60 seconds / 1 minute
)
```

### Sleep Data

Retrieving sleep data works in a similar way:

```python
from whoop_data import WhoopClient, get_sleep_data

# Create a client
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get sleep data for the last 7 days (default)
sleep_data = get_sleep_data(client=client)

# Or specify a date range
sleep_data = get_sleep_data(
    client=client,
    start_date="2023-01-01",
    end_date="2023-01-07"
)
```

### Comprehensive Cycle Data

Get all your metrics in one call - recovery, sleep, strain, and activities:

```python
from whoop_data import WhoopClient, get_cycle_data

# Create a client
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get comprehensive cycle data
cycles = get_cycle_data(client=client, start_date="2023-01-01", end_date="2023-01-07")

# Access all metrics
for cycle in cycles:
    print(f"Date: {cycle['date']}")
    print(f"Recovery Score: {cycle['recovery']['score']}%")
    print(f"HRV: {cycle['recovery']['hrv']} ms")
    print(f"Sleep Score: {cycle['sleep'][0]['score']}%")
    print(f"Day Strain: {cycle['strain']['day_strain']}")
    print(f"Workouts: {len(cycle['workouts'])}")
```

## Command Line Usage

```bash
# Extract heart rate data
python main.py --username your_email@example.com --password your_password --data-type heart_rate --from-date 2023-01-01 --to-date 2023-01-07

# Extract sleep data
python main.py --username your_email@example.com --password your_password --data-type sleep --from-date 2023-01-01 --to-date 2023-01-07

# Extract both sleep and heart rate data
python main.py --username your_email@example.com --password your_password --data-type all --from-date 2023-01-01 --to-date 2023-01-07
```

You can also store your credentials in a `.env` file:

```bash
WHOOP_USERNAME=your_email@example.com
WHOOP_PASSWORD=your_password
```

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md) - Detailed documentation of all API response formats with examples

## Examples

See the `examples/` directory for more usage examples:

- `examples/simple_example.py`: Minimal example showing basic usage
- `examples/comprehensive_data_example.py`: Example showing all metrics (recovery, sleep, strain, workouts)
- `examples/process_data.py`: Example of processing and visualizing HR data
- `examples/process_sleep.py`: Example of Sleep data and visualizing hypnogram

Here are some example visualizations from Whoop data:

![Heart Rate Plot](assets/heart_rate_plot.png)
*Example heart rate visualization showing 30 hours of data while writing this repo :)*

![Sleep Hypnogram](assets/sleep_hypnogram.png)
*Sleep stages hypnogram generated from sleep data*

## Contributing

Contributions are welcome! Here are some ways you can contribute:

- Report bugs or changes in API by raising an issue
- Implement missing features like activities, recovery, VOWs

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Whoop in any way. It is an independent project that uses the Whoop web app's internal API for data extraction. The API endpoints may change without notice.

## Acknowledgements

There are some github projects for reading the data, but they are a couple years old and the underlaying unofficial api structure changed over time. Then there is official dev api from Whoop, but they only provide aggregated information, which is not as cool as the raw hear rate in my opinion. Authentication logic and data relationships I got from [rharber/whoop_scraper](https://github.com/rharber/whoop_scraper/tree/master) repo.

*[AIDA (AI Disclosure Acknowledgement)](https://github.com/markwk/aida)*: Primarily Human. The following written content was written by me with the assistance of an AI-based system (CursorAI). Project started initially by me reverse engineering the flow pair programming with AI to create pypi library. Further updates use AI more as it is a lot faster at adapting to new endpoints and changes in API schema of Whoop App.
