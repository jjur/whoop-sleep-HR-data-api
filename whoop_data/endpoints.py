"""
Central repository for Whoop API endpoints.

This module contains all API endpoints used by the library,
making it easier to update when the API changes.
"""


class Endpoints:
    """
    Whoop API endpoints.
    
    This class centralizes all API endpoints used by the library.
    If the API endpoints change, they can be updated in one place.
    """
    # Base URLs
    BASE_API = "https://api-7.whoop.com"
    BASE_PROD = "https://api.prod.whoop.com"
    
    # Authentication
    AUTH = f"{BASE_API}/oauth/token"
    
    # Sleep endpoints
    SLEEP_EVENT = f"{BASE_PROD}/sleep-service/v1/sleep-events/v1-passthrough"
    SLEEP_VOW = f"{BASE_PROD}/vow-service/v1/vows/sleep/1d/cycle"
    
    # Activity endpoints
    CYCLES = f"{BASE_PROD}/activities-service/v1/cycles/aggregate/range"
    
    # Heart rate endpoints
    HEART_RATE = f"{BASE_PROD}/metrics-service/v1/metrics/user" 

    # Recovery endpoints
    RECOVERY_VOW = f"{BASE_PROD}/vow-service/v1/vows/recovery/1d/cycle"