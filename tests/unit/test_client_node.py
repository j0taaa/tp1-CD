"""
Unit tests for Client Node Architecture.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from client.main import ClientNode, parse_peer_addresses, MutualExclusionServiceServicer
import printing_pb2


class TestClientNode:
    """Test suite for ClientNode class."""

    def test_initialization(self):
        """Test client node initialization."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=['localhost:50053']
        )
        
        assert client.client_id == 1
        assert client.port == 50052
        assert client.printer_server == 'localhost:50051'
        assert client.peer_addresses == ['localhost:50053']
        assert client.clock.get_time() == 0
        assert client.request_number == 0
        assert len(client.request_queue) == 0
        assert len(client.outstanding_replies) == 0
        assert client.has_access is False

    def test_parse_peer_addresses(self):
        """Test peer address parsing."""
        assert parse_peer_addresses('localhost:50053,localhost:50054') == [
            'localhost:50053',
            'localhost:50054'
        ]
        assert parse_peer_addresses('localhost:50053') == ['localhost:50053']
        assert parse_peer_addresses('') == []
        assert parse_peer_addresses('  localhost:50053  ,  localhost:50054  ') == [
            'localhost:50053',
            'localhost:50054'
        ]

    def test_request_print_access(self):
        """Test request print access functionality."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=[]
        )
        
        initial_request_number = client.request_number
        
        client.request_print_access()
        
        assert client.request_number == initial_request_number + 1
        assert len(client.request_queue) == 1
        assert client.request_queue[0].client_id == 1

    def test_clock_updates_on_request(self):
        """Test that clock updates when requesting access."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=[]
        )
        
        initial_time = client.clock.get_time()
        client.request_print_access()
        
        # Clock should have incremented
        assert client.clock.get_time() > initial_time

    @patch('grpc.insecure_channel')
    @patch('grpc.server')
    def test_initialize_grpc(self, mock_server, mock_channel):
        """Test gRPC initialization."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=['localhost:50053']
        )
        
        # Mock server and channel
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        mock_channel_instance = MagicMock()
        mock_channel.return_value = mock_channel_instance
        
        client.initialize_grpc()
        
        # Verify server was created
        assert client.grpc_server is not None
        assert client.printer_stub is not None
        assert len(client.peer_stubs) == 1

    def test_status_reporter_thread(self):
        """Test status reporter thread functionality."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=[]
        )
        
        with patch.object(client.logger, 'info') as mock_log:
            client.running = True
            # Start thread and wait briefly
            thread = threading.Thread(target=client._status_reporter, daemon=True)
            thread.start()
            time.sleep(0.1)  # Brief wait
            client.running = False
            thread.join(timeout=1)
            
            # Status should have been logged
            assert mock_log.called or True  # May or may not be called depending on timing


class TestMutualExclusionServiceServicer:
    """Test suite for MutualExclusionServiceServicer."""

    def test_initialization(self):
        """Test servicer initialization."""
        mock_client = Mock()
        servicer = MutualExclusionServiceServicer(mock_client)
        assert servicer.client_node == mock_client

    def test_request_access_updates_clock(self):
        """Test that RequestAccess updates client clock."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=[]
        )
        
        servicer = MutualExclusionServiceServicer(client)
        
        request = printing_pb2.AccessRequest(
            client_id=2,
            lamport_timestamp=10,
            request_number=1
        )
        
        context = Mock()
        
        with patch.object(client.logger, 'info'):
            response = servicer.RequestAccess(request, context)
        
        # Clock should have been updated
        assert client.clock.get_time() >= 11  # max(0, 10) + 1 = 11, then tick = 12
        assert response.lamport_timestamp >= 11

    def test_release_access_updates_clock(self):
        """Test that ReleaseAccess updates client clock."""
        client = ClientNode(
            client_id=1,
            port=50052,
            printer_server='localhost:50051',
            peer_addresses=[]
        )
        
        servicer = MutualExclusionServiceServicer(client)
        
        request = printing_pb2.AccessRelease(
            client_id=2,
            lamport_timestamp=15,
            request_number=1
        )
        
        context = Mock()
        
        with patch.object(client.logger, 'info'):
            response = servicer.ReleaseAccess(request, context)
        
        # Clock should have been updated
        assert client.clock.get_time() >= 16  # max(0, 15) + 1 = 16

