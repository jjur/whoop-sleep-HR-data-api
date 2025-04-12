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
from whoop_data.logger import get_logger, WhoopLogger
import logging

# Export all important components
__all__ = [
    "WhoopClient",
    "get_sleep_data",
    "get_heart_rate_data",
    "save_to_json",
    "get_logger",
    "WhoopLogger",
    "set_debug_logging",
    "set_info_logging",
    "disable_logging",
]

# Helper functions for easier logger configuration
def set_debug_logging():
    """Enable debug logging for detailed request/response tracking"""
    get_logger().set_level(logging.DEBUG)
    
def set_info_logging():
    """Set default info logging level"""
    get_logger().set_level(logging.INFO)
    
def disable_logging():
    """Disable all logging"""
    get_logger().disable() 