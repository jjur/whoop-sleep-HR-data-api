"""
Whoop Client module combining authentication and API access.
"""
import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import time

from whoop_data.endpoints import Endpoints
from whoop_data.logger import get_logger

# Load environment variables if available
load_dotenv()

# Get logger instance
logger = get_logger()


class WhoopClient:
    """
    Handles authentication and interactions with the Whoop API.
    
    This class manages authentication, token handling, and API requests for the Whoop API.
    
    Example:
        >>> client = WhoopClient(username="your_email@example.com", password="your_password")
        >>> heart_rate_data = client.get_heart_rate(start="2023-01-01T00:00:00.000Z", end="2023-01-02T23:59:59.999Z")
    """
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize with credentials from arguments or environment variables.
        
        Args:
            username: Whoop account username/email (optional if set in environment)
            password: Whoop account password (optional if set in environment)
            
        Raises:
            ValueError: If credentials are not provided or invalid
        """
        self.username = username or os.getenv("WHOOP_USERNAME")
        self.password = password or os.getenv("WHOOP_PASSWORD")
        
        if not self.username or not self.password:
            logger.error("Whoop credentials not provided")
            raise ValueError(
                "Whoop credentials not provided. Use arguments or set WHOOP_USERNAME and WHOOP_PASSWORD environment variables."
            )
            
        self.userid: Optional[str] = None
        self.access_token: Optional[str] = None
        self.api_version = "7"
        
        logger.info("WhoopClient initialized")
        
        # Authenticate on initialization
        self.authenticate()
    
    def authenticate(self) -> None:
        """
        Authenticate with the Whoop API and get access token.
        
        Raises:
            Exception: If authentication fails
        """
        logger.info("Authenticating with Whoop API")
        
        auth_data = {
            "grant_type": "password",
            "issueRefresh": False,
            "password": self.password,
            "username": self.username,
        }
        
        # Log request (with sensitive data redacted)
        safe_auth_data = auth_data.copy()
        safe_auth_data["password"] = "[REDACTED]"
        logger.log_request("POST", Endpoints.AUTH, data=safe_auth_data)
        
        start_time = time.time()
        # Post credentials
        response = requests.post(
            Endpoints.AUTH,
            json=auth_data,
        )
        elapsed = time.time() - start_time
        
        # Log response
        logger.log_response(response.status_code, Endpoints.AUTH, elapsed)
        
        # Exit if authentication fails
        if response.status_code != 200:
            error_msg = f"Authentication failed: {response.status_code}"
            logger.error(error_msg)
            logger.error(f"Response: {response.text}")
            raise Exception(f"Authentication failed: Credentials rejected")

        # Extract and store authentication data
        auth_data = response.json()
        self.userid = auth_data["user"]["id"]
        self.access_token = auth_data["access_token"]
        logger.info(f"Successfully authenticated user {self.userid}")
    
    def get_auth_header(self) -> dict:
        """
        Returns the authorization header for API requests.
        
        Returns:
            dict: Authorization header
        """
        if not self.access_token:
            logger.info("Access token not available, authenticating")
            self.authenticate()
            
        return {
            "Authorization": f"Bearer {self.access_token}"
        }
        
    def refresh_if_needed(self, response: requests.Response) -> bool:
        """
        Check if authentication token needs to be refreshed.
        
        Args:
            response: Response object from a request
            
        Returns:
            bool: True if token was refreshed, False otherwise
        """
        if response.status_code in [401, 403]:
            logger.info("Token expired or invalid, refreshing...")
            self.authenticate()
            return True
        return False
    
    def _make_request(self, 
                     method: str, 
                     url: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     json_data: Optional[Dict[str, Any]] = None,
                     max_retries: int = 3) -> requests.Response:
        """
        Make a request to the Whoop API with automatic token refresh on 401/403.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            params: URL parameters
            json_data: JSON data for POST/PUT requests
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object
            
        Raises:
            Exception: If request fails after max retries
        """
        params = params or {}
            
        # Always include API version
        if "apiVersion" not in params:
            params["apiVersion"] = self.api_version
            
        headers = self.get_auth_header()
        
        retry_count = 0
        while retry_count < max_retries:
            # Log the request
            logger.log_request(method, url, params, headers, json_data)
            
            start_time = time.time()
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers
            )
            elapsed = time.time() - start_time
            
            # Log the response
            try:
                content = response.json() if response.content else None
            except:
                content = response.text if response.content else None
                
            logger.log_response(response.status_code, url, elapsed, content)
            
            # If unauthorized, try refreshing token and retry
            if response.status_code in [401, 403]:
                if self.refresh_if_needed(response):
                    headers = self.get_auth_header()
                    retry_count += 1
                    logger.info(f"Retrying request ({retry_count}/{max_retries})")
                    continue
            
            # Return response for all other cases
            return response
            
        # If we've exhausted retries
        error_msg = f"Request failed after {max_retries} retries"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def get_sleep_event(self, activity_id: str) -> Dict[str, Any]:
        """
        Get detailed sleep event data.
        
        Args:
            activity_id: Sleep activity ID
            
        Returns:
            Dict: Sleep event data
            
        Raises:
            Exception: If request fails
        """
        logger.info(f"Getting sleep event data for activity ID: {activity_id}")
        response = self._make_request(
            method="GET",
            url=Endpoints.SLEEP_EVENT,
            params={"activityId": activity_id}
        )
        
        if response.status_code == 200:
            logger.debug(f"Successfully retrieved sleep event data for activity ID: {activity_id}")
            return response.json()
        else:
            error_msg = f"Failed to get sleep event: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_sleep_vow(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get sleep vow data for a cycle.
        
        Args:
            cycle_id: Cycle ID
            
        Returns:
            Dict: Sleep vow data
            
        Raises:
            Exception: If request fails
        """
        logger.info(f"Getting sleep vow data for cycle ID: {cycle_id}")
        url = f"{Endpoints.SLEEP_VOW}/{cycle_id}"
        response = self._make_request(method="GET", url=url)
        
        if response.status_code == 200:
            logger.debug(f"Successfully retrieved sleep vow data for cycle ID: {cycle_id}")
            return response.json()
        else:
            error_msg = f"Failed to get sleep vow: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_cycles(self, 
                  start_time: str, 
                  end_time: str, 
                  limit: int = 26) -> List[Dict[str, Any]]:
        """
        Get cycle data for a date range.
        
        Args:
            start_time: Start time in ISO format
            end_time: End time in ISO format
            limit: Maximum number of cycles to retrieve
            
        Returns:
            List: Cycle data
            
        Raises:
            Exception: If request fails
        """
        logger.info(f"Getting cycle data from {start_time} to {end_time}")
        url = f"{Endpoints.CYCLES}/{self.userid}"
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }
        
        response = self._make_request(method="GET", url=url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully retrieved {len(data)} cycle records")
            return data
        else:
            error_msg = f"Failed to get cycles: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_heart_rate(self, 
                      start: str, 
                      end: str, 
                      step: int = 600) -> Dict[str, Any]:
        """
        Get heart rate data for a time range.
        
        Args:
            start: Start date/time in ISO format
            end: End date/time in ISO format
            step: Time step in seconds (6, 60, or 600)
            
        Returns:
            Dict: Heart rate data
        """
        logger.info(f"Getting heart rate data from {start} to {end} with step {step}")
        
        url = f"{Endpoints.HEART_RATE}/{self.userid}"
        response = self._make_request(
            method="GET",
            url=url,
            params={
                "start": start,
                "end": end,
                "step": step,
                "name": "heart_rate",   
            }
        )
        
        if response.status_code == 200:
            logger.debug(f"Successfully retrieved heart rate data from {start} to {end}")
            return response.json()
        else:
            error_msg = f"Failed to get heart rate data: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) 