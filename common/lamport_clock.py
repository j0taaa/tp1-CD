"""
Lamport Clock Implementation

Implements logical clocks as described by Leslie Lamport in "Time, Clocks, and the Ordering
of Events in a Distributed System".

Rules:
1. Before a local event: increment clock
2. Before sending a message: increment clock, attach timestamp to message
3. On receiving a message: merge clock with received timestamp (max(local, received) + 1)
"""

import threading
from typing import Optional


class LamportClock:
    """
    Thread-safe Lamport logical clock implementation.
    
    Thread safety is important as multiple threads may need to access/update
    the clock concurrently (e.g., one thread handling incoming requests,
    another generating local events).
    """

    def __init__(self, initial_time: int = 0):
        """
        Initialize Lamport clock.
        
        Args:
            initial_time: Starting timestamp (default: 0)
        """
        self._time = initial_time
        self._lock = threading.Lock()

    def tick(self) -> int:
        """
        Increment clock for a local event.
        
        Returns:
            New timestamp after incrementing
        """
        with self._lock:
            self._time += 1
            return self._time

    def send_event(self) -> int:
        """
        Increment clock before sending a message.
        Equivalent to tick() but semantically indicates a send operation.
        
        Returns:
            Timestamp to attach to outgoing message
        """
        return self.tick()

    def receive_event(self, received_timestamp: int) -> int:
        """
        Merge clock with received timestamp.
        
        Algorithm:
        - Take max(local_time, received_timestamp)
        - Increment by 1
        - Update local clock
        
        Args:
            received_timestamp: Timestamp received in message
            
        Returns:
            New local timestamp after merge
        """
        with self._lock:
            self._time = max(self._time, received_timestamp) + 1
            return self._time

    def get_time(self) -> int:
        """
        Get current timestamp without incrementing.
        
        Returns:
            Current timestamp
        """
        with self._lock:
            return self._time

    def update(self, new_time: int) -> int:
        """
        Manually update clock to a specific value.
        Useful for initialization or special cases.
        
        Args:
            new_time: New timestamp value
            
        Returns:
            Updated timestamp
        """
        with self._lock:
            self._time = new_time
            return self._time

    def __repr__(self) -> str:
        return f"LamportClock(time={self._time})"

    def __str__(self) -> str:
        return str(self._time)

