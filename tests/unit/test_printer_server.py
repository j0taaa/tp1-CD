"""
Unit tests for Printer Server implementation.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
import grpc
from concurrent import futures
import printing_pb2
import printing_pb2_grpc
from printer.server import PrintingServiceServicer


class TestPrintingServiceServicer:
    """Test suite for PrintingServiceServicer."""

    def test_initialization(self):
        """Test servicer initialization."""
        servicer = PrintingServiceServicer()
        assert servicer.print_delay_min == 2.0
        assert servicer.print_delay_max == 3.0
        assert servicer.clock.get_time() == 0

    def test_initialization_custom_delays(self):
        """Test servicer initialization with custom delays."""
        servicer = PrintingServiceServicer(print_delay_min=1.0, print_delay_max=2.0)
        assert servicer.print_delay_min == 1.0
        assert servicer.print_delay_max == 2.0

    def test_send_to_printer_updates_clock(self):
        """Test that SendToPrinter updates Lamport clock correctly."""
        servicer = PrintingServiceServicer(print_delay_min=0.01, print_delay_max=0.02)
        
        request = printing_pb2.PrintRequest(
            client_id=1,
            message_content="Test",
            lamport_timestamp=5,
            request_number=1
        )
        
        context = Mock()
        
        # Mock the logger to avoid print output during tests
        with patch.object(servicer.logger, 'print_request'), \
             patch.object(servicer.logger, 'log'), \
             patch.object(servicer.logger, 'info'):
            
            response = servicer.SendToPrinter(request, context)
        
        # Clock should be updated: max(0, 5) + 1 = 6, then tick for response = 7
        assert servicer.clock.get_time() >= 6
        assert response.lamport_timestamp >= 6

    def test_send_to_printer_response_format(self):
        """Test that SendToPrinter returns correct response format."""
        servicer = PrintingServiceServicer(print_delay_min=0.01, print_delay_max=0.02)
        
        request = printing_pb2.PrintRequest(
            client_id=1,
            message_content="Test message",
            lamport_timestamp=10,
            request_number=1
        )
        
        context = Mock()
        
        with patch.object(servicer.logger, 'print_request'), \
             patch.object(servicer.logger, 'log'), \
             patch.object(servicer.logger, 'info'):
            
            response = servicer.SendToPrinter(request, context)
        
        assert isinstance(response, printing_pb2.PrintResponse)
        assert response.success is True
        assert "sucesso" in response.confirmation_message.lower()
        assert response.lamport_timestamp > 0

    def test_send_to_printer_simulates_delay(self):
        """Test that SendToPrinter simulates printing delay."""
        servicer = PrintingServiceServicer(print_delay_min=0.1, print_delay_max=0.2)
        
        request = printing_pb2.PrintRequest(
            client_id=1,
            message_content="Test",
            lamport_timestamp=1,
            request_number=1
        )
        
        context = Mock()
        
        with patch.object(servicer.logger, 'print_request'), \
             patch.object(servicer.logger, 'log'), \
             patch.object(servicer.logger, 'info'):
            
            start_time = time.time()
            response = servicer.SendToPrinter(request, context)
            elapsed = time.time() - start_time
        
        # Should have delayed at least the minimum delay
        assert elapsed >= 0.1
        assert response.success is True

    def test_send_to_printer_logs_message(self, capsys):
        """Test that SendToPrinter logs messages correctly."""
        servicer = PrintingServiceServicer(print_delay_min=0.01, print_delay_max=0.02)
        
        request = printing_pb2.PrintRequest(
            client_id=42,
            message_content="Hello World",
            lamport_timestamp=100,
            request_number=1
        )
        
        context = Mock()
        
        # Don't mock logger - let it print to verify format
        with patch('time.sleep'):  # Skip actual delay
            response = servicer.SendToPrinter(request, context)
        
        captured = capsys.readouterr()
        
        # Check that output contains expected format
        assert "[TS: 100]" in captured.out
        assert "CLIENTE 42" in captured.out
        assert "Hello World" in captured.out

    def test_multiple_requests_update_clock(self):
        """Test that multiple requests properly update clock."""
        servicer = PrintingServiceServicer(print_delay_min=0.01, print_delay_max=0.02)
        
        context = Mock()
        
        with patch.object(servicer.logger, 'print_request'), \
             patch.object(servicer.logger, 'log'), \
             patch.object(servicer.logger, 'info'):
            
            # First request
            request1 = printing_pb2.PrintRequest(
                client_id=1,
                message_content="First",
                lamport_timestamp=5,
                request_number=1
            )
            response1 = servicer.SendToPrinter(request1, context)
            time1 = servicer.clock.get_time()
            
            # Second request with higher timestamp
            request2 = printing_pb2.PrintRequest(
                client_id=2,
                message_content="Second",
                lamport_timestamp=20,
                request_number=1
            )
            response2 = servicer.SendToPrinter(request2, context)
            time2 = servicer.clock.get_time()
        
        # Clock should have increased
        assert time2 > time1
        # Response2 timestamp should be greater than response1
        assert response2.lamport_timestamp > response1.lamport_timestamp

