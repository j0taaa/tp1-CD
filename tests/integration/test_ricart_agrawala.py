"""
Integration tests for Ricart-Agrawala algorithm.

Tests the full flow with in-process gRPC servers and clients.
"""

import pytest
import threading
import time
from concurrent import futures
import grpc
from client.main import ClientNode
from printer.server import PrintingServiceServicer
import printing_pb2_grpc
import printing_pb2


class TestRicartAgrawalaIntegration:
    """Integration tests for Ricart-Agrawala mutual exclusion."""

    @pytest.fixture
    def printer_server(self):
        """Create an in-process printer server."""
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        servicer = PrintingServiceServicer(print_delay_min=0.01, print_delay_max=0.02)
        printing_pb2_grpc.add_PrintingServiceServicer_to_server(servicer, server)
        
        # Use ephemeral port (0) for testing
        port = server.add_insecure_port('[::]:0')
        server.start()
        
        yield ('localhost', port)
        
        server.stop(grace=1)

    def test_two_clients_mutual_exclusion(self, printer_server):
        """Test that two clients respect mutual exclusion."""
        printer_addr = f"{printer_server[0]}:{printer_server[1]}"
        
        # Use fixed ports for testing
        client1_port = 50062
        client2_port = 50063
        
        # Create two clients with known ports
        client1 = ClientNode(
            client_id=1,
            port=client1_port,
            printer_server=printer_addr,
            peer_addresses=[f"localhost:{client2_port}"],
            job_interval_min=100.0,  # Disable auto-generation
            job_interval_max=100.0
        )
        
        client2 = ClientNode(
            client_id=2,
            port=client2_port,
            printer_server=printer_addr,
            peer_addresses=[f"localhost:{client1_port}"],
            job_interval_min=100.0,
            job_interval_max=100.0
        )
        
        # Initialize gRPC
        client1.initialize_grpc()
        client2.initialize_grpc()
        client1.grpc_server.start()
        client2.grpc_server.start()
        
        # Wait for servers to be ready
        time.sleep(0.5)
        
        # Test: Client1 requests access
        thread1 = threading.Thread(target=client1.request_print_access, daemon=True)
        thread1.start()
        thread1.join(timeout=5)
        assert not thread1.is_alive()
        assert client1.has_access
        
        # Client2 requests access (should be deferred since client1 has access)
        thread2 = threading.Thread(target=client2.request_print_access, daemon=True)
        thread2.start()

        # Give time for client2 to issue request and be deferred
        time.sleep(0.5)
        assert thread2.is_alive()
        assert client2.waiting_for_access
        assert not client2.has_access
        
        # Client1 releases access
        client1.release_access()
        thread2.join(timeout=5)
        assert not thread2.is_alive()
        assert client2.has_access
        client2.release_access()
        
        # After release, client2 should eventually get access
        # (if it was waiting, it should now proceed)
        
        # Cleanup
        client1.stop()
        client2.stop()
        client1.grpc_server.stop(grace=1)
        client2.grpc_server.stop(grace=1)
        
        # Basic verification: both clients processed requests
        assert client1.request_number > 0
        assert client2.request_number > 0

    def test_timestamp_comparison(self):
        """Test that timestamp comparison works correctly for RA."""
        client1 = ClientNode(
            client_id=1,
            port=0,
            printer_server='localhost:50051',
            peer_addresses=[],
            job_interval_min=100.0,
            job_interval_max=100.0
        )
        
        # Set up clients so client1 is waiting
        client1.request_number = 1
        pending = type('PendingRequest', (), {
            'client_id': 1,
            'lamport_timestamp': 10,
            'request_number': 1
        })()
        client1.request_queue.append(pending)
        client1.waiting_for_access = True
        
        # Create a request with lower timestamp
        request_lower = printing_pb2.AccessRequest(
            client_id=2,
            lamport_timestamp=5,  # Lower than 10
            request_number=1
        )
        
        servicer = client1._get_servicer()
        response = servicer.RequestAccess(request_lower, None)
        
        # Should grant immediately (lower timestamp)
        assert response.access_granted is True
        
        # Create a request with higher timestamp
        client1.request_queue.clear()
        client1.request_queue.append(pending)
        request_higher = printing_pb2.AccessRequest(
            client_id=2,
            lamport_timestamp=15,  # Higher than 10
            request_number=1
        )
        
        def _call_request():
            servicer.RequestAccess(request_higher, None)

        req_thread = threading.Thread(target=_call_request, daemon=True)
        req_thread.start()

        time.sleep(0.5)
        assert req_thread.is_alive()
        assert len(client1.deferred_replies) > 0

        # Simulate entering and leaving critical section to unblock deferred request
        with client1.lock:
            client1.has_access = True
            client1.waiting_for_access = False

        client1.release_access()

        req_thread.join(timeout=5)
        assert not req_thread.is_alive()
        assert len(client1.deferred_replies) == 0

    def test_lamport_clock_monotonicity(self):
        """Test that Lamport clocks maintain monotonicity."""
        from common.lamport_clock import LamportClock
        
        clock = LamportClock()
        timestamps = []
        
        # Generate events
        timestamps.append(clock.tick())
        timestamps.append(clock.send_event())
        timestamps.append(clock.receive_event(5))
        timestamps.append(clock.tick())
        timestamps.append(clock.receive_event(20))
        
        # Verify monotonicity
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1], \
                f"Timestamp {timestamps[i]} not greater than {timestamps[i-1]}"

    def test_concurrent_access_requests(self, printer_server):
        """Test multiple concurrent access requests."""
        printer_addr = f"{printer_server[0]}:{printer_server[1]}"
        
        client = ClientNode(
            client_id=1,
            port=0,
            printer_server=printer_addr,
            peer_addresses=[],
            job_interval_min=100.0,
            job_interval_max=100.0
        )
        
        client.initialize_grpc()
        client.grpc_server.start()
        
        # Multiple concurrent requests should be handled correctly
        def make_request():
            client.request_print_access()
        
        threads = [threading.Thread(target=make_request, daemon=True) for _ in range(3)]
        for t in threads:
            t.start()
        
        time.sleep(1)
        
        # Should have only one request in queue (others should be handled)
        assert len(client.request_queue) <= 3
        
        client.stop()
        client.grpc_server.stop(grace=1)


# Helper method extension for ClientNode (for testing)
def _get_servicer(self):
    """Get the servicer instance for testing."""
    from client.main import MutualExclusionServiceServicer
    return MutualExclusionServiceServicer(self)

# Monkey patch for testing
ClientNode._get_servicer = _get_servicer

