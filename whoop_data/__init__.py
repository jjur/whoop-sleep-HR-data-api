"""
Whoop Data - A library to extract sleep and heart rate data from Whoop.

This library provides simple functions to authenticate with the Whoop API
and retrieve sleep and heart rate data.
"""

__version__ = "0.1.0"

# Import core components for easy access
from whoop_data.client import WhoopClient
from whoop_data.data import (
    get_sleep_data,
    get_heart_rate_data,
    save_to_json
)

# Export all important components
__all__ = [
    "WhoopClient",
    "get_sleep_data",
    "get_heart_rate_data",
    "save_to_json",
] 