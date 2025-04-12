"""
Whoop Client module combining authentication and API access.
"""
import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from whoop_data.endpoints import Endpoints

# Load environment variables if available
load_dotenv()


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
            raise ValueError(
                "Whoop credentials not provided. Use arguments or set WHOOP_USERNAME and WHOOP_PASSWORD environment variables."
            )
            
        self.userid: Optional[str] = None
        self.access_token: Optional[str] = None
        self.api_version = "7"
        
        # Authenticate on initialization
        self.authenticate()
    
    def authenticate(self) -> None:
        """
        Authenticate with the Whoop API and get access token.
        
        Raises:
            Exception: If authentication fails
        """
        # Post credentials
        response = requests.post(
            Endpoints.AUTH,
            json={
                "grant_type": "password",
                "issueRefresh": False,
                "password": self.password,
                "username": self.username,
            },
        )
        
        # Exit if authentication fails
        if response.status_code != 200:
            print(f"Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Authentication failed: Credentials rejected")

        # Extract and store authentication data
        auth_data = response.json()
        self.userid = auth_data["user"]["id"]
        self.access_token = auth_data["access_token"]
        print(f"Successfully authenticated user {self.userid}")
    
    def get_auth_header(self) -> dict:
        """
        Returns the authorization header for API requests.
        
        Returns:
            dict: Authorization header
        """
        if not self.access_token:
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
            print("Token expired or invalid, refreshing...")
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
        # Ensure we have valid params
        if params is None:
            params = {}
            
        # Always include API version
        if "apiVersion" not in params:
            params["apiVersion"] = self.api_version
            
        headers = self.get_auth_header()
        
        retry_count = 0
        while retry_count < max_retries:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers
            )
            
            # If unauthorized, try refreshing token and retry
            if response.status_code in [401, 403]:
                if self.refresh_if_needed(response):
                    headers = self.get_auth_header()
                    retry_count += 1
                    continue
            
            # Return response for all other cases
            return response
            
        # If we've exhausted retries
        raise Exception(f"Request failed after {max_retries} retries")
    
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
        response = self._make_request(
            method="GET",
            url=Endpoints.SLEEP_EVENT,
            params={"activityId": activity_id}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get sleep event: {response.status_code} - {response.text}")
    
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
        url = f"{Endpoints.SLEEP_VOW}/{cycle_id}"
        response = self._make_request(method="GET", url=url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get sleep vow: {response.status_code} - {response.text}")
    
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
        url = f"{Endpoints.CYCLES}/{self.userid}"
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }
        
        response = self._make_request(method="GET", url=url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get cycles: {response.status_code} - {response.text}")
    
    def get_heart_rate(self, 
                      start: str, 
                      end: str, 
                      step: int = 600) -> Dict[str, Any]:
        """
        Get heart rate data for a time range.
        
        Args:
            start: Start time in ISO format
            end: End time in ISO format
            step: Time step in seconds (default: 600 = 10 minutes)
            
        Returns:
            Dict: Heart rate data
            
        Raises:
            Exception: If request fails
        """
        url = f"{Endpoints.HEART_RATE}/{self.userid}"
        params = {
            "start": start,
            "end": end,
            "name": "heart_rate",
            "order": "t",
            "step": step
        }
        
        response = self._make_request(method="GET", url=url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get heart rate data: {response.status_code} - {response.text}") 