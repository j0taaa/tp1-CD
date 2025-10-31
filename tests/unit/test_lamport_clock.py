"""
Unit tests for Lamport Clock implementation.
"""

import pytest
import threading
from common.lamport_clock import LamportClock


class TestLamportClock:
    """Test suite for LamportClock class."""

    def test_initialization(self):
        """Test clock initialization."""
        clock = LamportClock()
        assert clock.get_time() == 0

        clock2 = LamportClock(initial_time=5)
        assert clock2.get_time() == 5

    def test_tick(self):
        """Test local event increment."""
        clock = LamportClock()
        assert clock.tick() == 1
        assert clock.get_time() == 1
        assert clock.tick() == 2
        assert clock.get_time() == 2

    def test_send_event(self):
        """Test send event increment."""
        clock = LamportClock()
        timestamp = clock.send_event()
        assert timestamp == 1
        assert clock.get_time() == 1

    def test_receive_event(self):
        """Test receive event merge."""
        clock = LamportClock(initial_time=5)
        
        # Receive timestamp less than current
        new_time = clock.receive_event(3)
        assert new_time == 6  # max(5, 3) + 1 = 6
        assert clock.get_time() == 6

        # Receive timestamp greater than current
        new_time = clock.receive_event(10)
        assert new_time == 11  # max(6, 10) + 1 = 11
        assert clock.get_time() == 11

        # Receive timestamp equal to current
        new_time = clock.receive_event(11)
        assert new_time == 12  # max(11, 11) + 1 = 12

    def test_thread_safety(self):
        """Test thread safety of clock operations."""
        clock = LamportClock()
        results = []

        def worker():
            for _ in range(100):
                clock.tick()

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have incremented 500 times (5 threads * 100 increments)
        assert clock.get_time() == 500

    def test_update(self):
        """Test manual clock update."""
        clock = LamportClock()
        clock.update(42)
        assert clock.get_time() == 42

    def test_str_repr(self):
        """Test string representation."""
        clock = LamportClock(initial_time=5)
        assert str(clock) == "5"
        assert "LamportClock" in repr(clock)
        assert "5" in repr(clock)

