# Whoop Data API

A simple Python library to access Whoop's internal web app API for extracting sleep and heart rate data.

> **Note**: This is an unofficial library based on reverse-engineered API endpoints and is not affiliated with or endorsed by Whoop. The API endpoints may change without notice.

## Features

- Authenticate with Whoop using your account credentials
- Extract detailed sleep data including sleep stages, disturbances, and metrics
- Extract heart rate data with customizable time intervals
- Simple, user-friendly API that follows DRY and KISS principles
- Easy-to-use command line interface
- Environment variable support for credentials

## Installation

```bash
# From PyPI (coming soon)
pip install whoop-data

# From source
git clone https://github.com/yourusername/whoop-sleep-HR-data-api.git
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
    step=300  # 5 minutes
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
- `examples/get_heart_rate_data.py`: Example of extracting heart rate data
- `examples/get_sleep_data.py`: Example of extracting sleep data
- `examples/get_all_data.py`: Example of extracting both sleep and heart rate data
- `examples/process_data.py`: Example of processing and visualizing data

## Data Processing Example

The library makes it easy to analyze your data:

```python
import pandas as pd
import matplotlib.pyplot as plt
from whoop_data import WhoopClient, get_heart_rate_data

# Get data
client = WhoopClient()
hr_data = get_heart_rate_data(client)

# Convert to pandas DataFrame
df = pd.DataFrame(hr_data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Calculate statistics
avg_hr = df['heart_rate'].mean()
max_hr = df['heart_rate'].max()
min_hr = df['heart_rate'].min()

print(f"Average HR: {avg_hr:.1f} bpm, Max: {max_hr} bpm, Min: {min_hr} bpm")

# Create a visualization
plt.figure(figsize=(10, 5))
plt.plot(df.index, df['heart_rate'])
plt.title('Heart Rate Over Time')
plt.ylabel('Heart Rate (bpm)')
plt.grid(True)
plt.savefig('heart_rate_chart.png')
```

## Library Structure

The library is organized into modules for easy maintenance and extensibility:

- `whoop_data/client.py`: Combined client for authentication and API access
- `whoop_data/endpoints.py`: Centralized API endpoints
- `whoop_data/data.py`: Data processing functions

## License

MIT License - See LICENSE file for details.

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Whoop in any way. It is an independent project that uses the Whoop web app's internal API for data extraction. The API endpoints may change without notice.
