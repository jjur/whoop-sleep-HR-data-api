# Whoop Data API

A simple Python library to access Whoop's internal web app API for extracting sleep and heart rate data.

> **Note**: This is an unofficial library based on reverse-engineered API endpoints and is not affiliated with or endorsed by Whoop. The API endpoints may change without notice.

## Features

- Authenticate with Whoop using your account credentials
- Extract data from app.whoop.com using internal API:
  - Sleep data including sleep stages, disturbances, and metrics
  - Heart rate data with customizable time intervals

### Not yet implemented
- Reading of all Activies
- Whoop recommendations / VOWs

## Installation

```bash
# From PyPI
pip install whoop-data

# From source
git clone https://github.com/jjur/whoop-sleep-HR-data-api.git
cd whoop-sleep-HR-data-api
pip install -r requirements.txt .
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

```
WHOOP_USERNAME=your_email@example.com
WHOOP_PASSWORD=your_password
```

## Examples

See the `examples/` directory for more usage examples:

- `examples/simple_example.py`: Minimal example showing basic usage
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
There are some github projects for reading the data, but they are a couple years old and the underlaying unofficial api structure changed over time. Then there is official dev api from Whoop, but they only provide aggregated information, which is not as cool as the raw hear rate in my opinion. Authentication logic and data relationships I got from [https://github.com/rharber/whoop_scraper/tree/master](rharber/whoop_scraper) repo. 
