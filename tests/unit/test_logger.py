"""
Unit tests for Logger implementation.
"""

import pytest
from common.logger import Logger, create_client_logger, create_server_logger


class TestLogger:
    """Test suite for Logger class."""

    def test_client_logger_format(self, capsys):
        """Test client logger message formatting."""
        logger = Logger(client_id=1)
        logger.log("Test message", lamport_timestamp=42)
        captured = capsys.readouterr()
        assert "[TS: 42]" in captured.out
        assert "CLIENTE 1" in captured.out
        assert "Test message" in captured.out

    def test_server_logger_format(self, capsys):
        """Test server logger message formatting."""
        logger = Logger()
        logger.log("Server message", lamport_timestamp=42)
        captured = capsys.readouterr()
        assert "[TS: 42]" in captured.out
        assert "SERVIDOR" in captured.out
        assert "Server message" in captured.out

    def test_log_levels(self, capsys):
        """Test different log levels."""
        logger = Logger(client_id=1)
        
        logger.info("Info message", lamport_timestamp=1)
        logger.warning("Warning message", lamport_timestamp=2)
        logger.error("Error message", lamport_timestamp=3)
        logger.debug("Debug message", lamport_timestamp=4)
        
        captured = capsys.readouterr()
        assert "INFO:" in captured.out
        assert "WARNING:" in captured.out
        assert "ERROR:" in captured.out
        assert "DEBUG:" in captured.out

    def test_print_request(self, capsys):
        """Test print_request method."""
        logger = Logger(client_id=1)
        logger.print_request("Print content", lamport_timestamp=100)
        captured = capsys.readouterr()
        assert "[TS: 100]" in captured.out
        assert "Print content" in captured.out

    def test_factory_functions(self):
        """Test factory functions."""
        client_logger = create_client_logger(5)
        assert client_logger.client_id == 5

        server_logger = create_server_logger()
        assert server_logger.client_id is None

