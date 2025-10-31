"""
Unit tests for MessageBuilder utilities.
"""

import pytest
import printing_pb2
from common.message_builder import MessageBuilder


class TestMessageBuilder:
    """Test suite for MessageBuilder class."""

    def test_build_print_request(self):
        """Test PrintRequest message building."""
        msg = MessageBuilder.build_print_request(
            client_id=1,
            message_content="Test",
            lamport_timestamp=42,
            request_number=5,
        )
        assert isinstance(msg, printing_pb2.PrintRequest)
        assert msg.client_id == 1
        assert msg.message_content == "Test"
        assert msg.lamport_timestamp == 42
        assert msg.request_number == 5

    def test_build_print_response(self):
        """Test PrintResponse message building."""
        msg = MessageBuilder.build_print_response(
            success=True,
            confirmation_message="Printed",
            lamport_timestamp=43,
        )
        assert isinstance(msg, printing_pb2.PrintResponse)
        assert msg.success is True
        assert msg.confirmation_message == "Printed"
        assert msg.lamport_timestamp == 43

    def test_build_access_request(self):
        """Test AccessRequest message building."""
        msg = MessageBuilder.build_access_request(
            client_id=2,
            lamport_timestamp=44,
            request_number=6,
        )
        assert isinstance(msg, printing_pb2.AccessRequest)
        assert msg.client_id == 2
        assert msg.lamport_timestamp == 44
        assert msg.request_number == 6

    def test_build_access_response(self):
        """Test AccessResponse message building."""
        msg = MessageBuilder.build_access_response(
            access_granted=True,
            lamport_timestamp=45,
        )
        assert isinstance(msg, printing_pb2.AccessResponse)
        assert msg.access_granted is True
        assert msg.lamport_timestamp == 45

    def test_build_access_release(self):
        """Test AccessRelease message building."""
        msg = MessageBuilder.build_access_release(
            client_id=3,
            lamport_timestamp=46,
            request_number=7,
        )
        assert isinstance(msg, printing_pb2.AccessRelease)
        assert msg.client_id == 3
        assert msg.lamport_timestamp == 46
        assert msg.request_number == 7

    def test_build_empty(self):
        """Test Empty message building."""
        msg = MessageBuilder.build_empty()
        assert isinstance(msg, printing_pb2.Empty)

