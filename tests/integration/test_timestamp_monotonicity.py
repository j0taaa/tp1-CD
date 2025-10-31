"""
Tests for timestamp monotonicity verification.
"""

import pytest
from common.lamport_clock import LamportClock
from client.main import ClientNode
import threading
import time


class TestTimestampMonotonicity:
    """Test that Lamport timestamps maintain monotonicity."""

    def test_lamport_clock_monotonicity_basic(self):
        """Test basic monotonicity in Lamport clock."""
        clock = LamportClock()
        timestamps = []
        
        # Sequence of events
        timestamps.append(clock.tick())  # Local event
        timestamps.append(clock.send_event())  # Send event
        timestamps.append(clock.receive_event(5))  # Receive with TS 5
        timestamps.append(clock.tick())  # Another local event
        timestamps.append(clock.receive_event(20))  # Receive with TS 20
        
        # All timestamps should be monotonically increasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1], \
                f"Monotonicity violated: {timestamps[i]} <= {timestamps[i-1]}"

    def test_lamport_clock_thread_safety_monotonicity(self):
        """Test monotonicity under concurrent access."""
        clock = LamportClock()
        timestamps = []
        lock = threading.Lock()
        
        def increment_clock():
            for _ in range(10):
                ts = clock.tick()
                with lock:
                    timestamps.append(ts)
        
        threads = [threading.Thread(target=increment_clock) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify monotonicity
        sorted_timestamps = sorted(timestamps)
        assert timestamps == sorted_timestamps, \
            "Timestamps not monotonic under concurrent access"

    def test_client_timestamps_monotonicity(self):
        """Test that client operations maintain timestamp monotonicity."""
        client = ClientNode(
            client_id=1,
            port=0,
            printer_server='localhost:50051',
            peer_addresses=[],
            job_interval_min=100.0,
            job_interval_max=100.0
        )
        
        timestamps = []
        
        # Simulate sequence of operations
        ts1 = client.clock.tick()
        timestamps.append(ts1)
        
        ts2 = client.clock.send_event()
        timestamps.append(ts2)
        
        ts3 = client.clock.receive_event(10)
        timestamps.append(ts3)
        
        ts4 = client.clock.send_event()
        timestamps.append(ts4)
        
        # Verify monotonicity
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1], \
                f"Client timestamp monotonicity violated: {timestamps[i]} <= {timestamps[i-1]}"

    def test_request_response_cycle_monotonicity(self):
        """Test monotonicity through request/response cycle."""
        client = ClientNode(
            client_id=1,
            port=0,
            printer_server='localhost:50051',
            peer_addresses=[],
            job_interval_min=100.0,
            job_interval_max=100.0
        )
        
        timestamps = []
        
        # Request access
        client.request_number = 1
        client.request_queue.clear()
        ts_req = client.clock.send_event()
        timestamps.append(ts_req)
        
        # Simulate receiving access request
        import printing_pb2
        request = printing_pb2.AccessRequest(
            client_id=2,
            lamport_timestamp=5,
            request_number=1
        )
        
        from client.main import MutualExclusionServiceServicer
        servicer = MutualExclusionServiceServicer(client)
        response = servicer.RequestAccess(request, None)
        
        timestamps.append(response.lamport_timestamp)
        
        # Simulate release
        release = printing_pb2.AccessRelease(
            client_id=2,
            lamport_timestamp=15,
            request_number=1
        )
        servicer.ReleaseAccess(release, None)
        
        ts_after_release = client.clock.get_time()
        timestamps.append(ts_after_release)
        
        # Verify monotonicity
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1], \
                f"Request/response cycle monotonicity violated"

