"""
Logging functionality for whoop-data library.

This module provides a configurable logger for tracking API requests, responses,
and other events in the library.
"""
import logging
import sys
from typing import Optional, Dict, Any

# Global logger configuration is removed to prevent double logging


class WhoopLogger:
    """
    Configurable logger for the whoop-data library.
    
    This logger can be configured to log at different levels and can be
    enabled/disabled as needed.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(WhoopLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger if it hasn't been initialized yet"""
        if not WhoopLogger._initialized:
            self.logger = logging.getLogger("whoop_data")
            # Prevent adding handlers if they already exist
            if not self.logger.handlers:
                self.handler = logging.StreamHandler(sys.stdout)
                self.handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    '%Y-%m-%d %H:%M:%S'
                ))
                self.logger.addHandler(self.handler)
            self.logger.setLevel(logging.INFO)
            # Prevent propagation to root logger to avoid double logging
            self.logger.propagate = False
            self.enabled = True
            WhoopLogger._initialized = True
    
    def set_level(self, level: int) -> None:
        """
        Set the logging level.
        
        Args:
            level: Logging level (e.g., logging.DEBUG, logging.INFO)
        """
        self.logger.setLevel(level)
    
    def enable(self) -> None:
        """Enable logging"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable logging"""
        self.enabled = False
    
    def debug(self, message: str) -> None:
        """Log a debug message"""
        if self.enabled:
            self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log an info message"""
        if self.enabled:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message"""
        if self.enabled:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message"""
        if self.enabled:
            self.logger.error(message)
    
    def log_request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None, 
                   headers: Optional[Dict[str, Any]] = None, data: Optional[Any] = None) -> None:
        """
        Log an HTTP request.
        
        Args:
            method: HTTP method
            url: Request URL
            params: Request parameters
            headers: Request headers
            data: Request data
        """
        if not self.enabled:
            return
            
        # Don't log the full Authorization header
        if headers and 'Authorization' in headers:
            safe_headers = headers.copy()
            safe_headers['Authorization'] = 'Bearer [REDACTED]'
        else:
            safe_headers = headers
            
        self.logger.debug(f"REQUEST: {method} {url}")
        if params:
            self.logger.debug(f"REQUEST PARAMS: {params}")
        if safe_headers:
            self.logger.debug(f"REQUEST HEADERS: {safe_headers}")
        if data:
            self.logger.debug(f"REQUEST DATA: {data}")
    
    def log_response(self, status_code: int, url: str, elapsed: float, 
                    content: Optional[str] = None) -> None:
        """
        Log an HTTP response.
        
        Args:
            status_code: HTTP status code
            url: Request URL
            elapsed: Response time in seconds
            content: Response content
        """
        if not self.enabled:
            return
            
        self.logger.debug(f"RESPONSE: {status_code} from {url} ({elapsed:.2f}s)")
        if content and self.logger.level <= logging.DEBUG:
            # Truncate very long responses
            if len(str(content)) > 1000:
                self.logger.debug(f"RESPONSE CONTENT: {str(content)[:1000]}... [truncated]")
            else:
                self.logger.debug(f"RESPONSE CONTENT: {content}")


# Create a global instance
whoop_logger = WhoopLogger()


def get_logger() -> WhoopLogger:
    """
    Get the global logger instance.
    
    Returns:
        WhoopLogger: The global logger instance
    """
    return whoop_logger 