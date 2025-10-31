"""
Logging Utilities

Provides standardized logging format for the distributed printing system.
Format: [TS: {timestamp}] CLIENTE {id}: {message}
"""

import sys
from datetime import datetime
from typing import Optional


class Logger:
    """
    Standardized logger for distributed printing system.
    
    Provides consistent message formatting as specified:
    Format: [TS: {timestamp}] CLIENTE {id}: {message}
    
    For server messages (no client_id):
    Format: [TS: {timestamp}] SERVIDOR: {message}
    """

    def __init__(self, client_id: Optional[int] = None):
        """
        Initialize logger.
        
        Args:
            client_id: Client ID for client loggers, None for server logger
        """
        self.client_id = client_id

    def _format_message(self, message: str, lamport_timestamp: Optional[int] = None) -> str:
        """
        Format message according to specification.
        
        Args:
            message: Message content
            lamport_timestamp: Lamport logical timestamp (if None, uses system time)
            
        Returns:
            Formatted message string
        """
        if lamport_timestamp is not None:
            timestamp = lamport_timestamp
        else:
            # Fallback to system time if no Lamport timestamp provided
            timestamp = int(datetime.now().timestamp() * 1000)

        if self.client_id is not None:
            return f"[TS: {timestamp}] CLIENTE {self.client_id}: {message}"
        else:
            return f"[TS: {timestamp}] SERVIDOR: {message}"

    def log(self, message: str, lamport_timestamp: Optional[int] = None):
        """
        Log a message with standardized format.
        
        Args:
            message: Message to log
            lamport_timestamp: Optional Lamport timestamp to include
        """
        formatted = self._format_message(message, lamport_timestamp)
        print(formatted, flush=True)

    def info(self, message: str, lamport_timestamp: Optional[int] = None):
        """Log info message."""
        self.log(f"INFO: {message}", lamport_timestamp)

    def error(self, message: str, lamport_timestamp: Optional[int] = None):
        """Log error message."""
        self.log(f"ERROR: {message}", lamport_timestamp)

    def warning(self, message: str, lamport_timestamp: Optional[int] = None):
        """Log warning message."""
        self.log(f"WARNING: {message}", lamport_timestamp)

    def debug(self, message: str, lamport_timestamp: Optional[int] = None):
        """Log debug message (can be disabled in production)."""
        self.log(f"DEBUG: {message}", lamport_timestamp)

    def print_request(self, message_content: str, lamport_timestamp: Optional[int] = None):
        """
        Log print request message (for server).
        
        Args:
            message_content: Content to print
            lamport_timestamp: Lamport timestamp from request
        """
        formatted = self._format_message(message_content, lamport_timestamp)
        print(formatted, flush=True)


def create_client_logger(client_id: int) -> Logger:
    """
    Factory function to create a client logger.
    
    Args:
        client_id: Client identifier
        
    Returns:
        Logger instance configured for the client
    """
    return Logger(client_id=client_id)


def create_server_logger() -> Logger:
    """
    Factory function to create a server logger.
    
    Returns:
        Logger instance configured for the server
    """
    return Logger(client_id=None)

