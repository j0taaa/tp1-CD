"""
Message Serialization Helpers

Utilities for converting between gRPC messages and internal data structures.
"""

from typing import Optional
import printing_pb2


class MessageBuilder:
    """
    Helper class for building gRPC messages with proper Lamport timestamp handling.
    """

    @staticmethod
    def build_print_request(
        client_id: int,
        message_content: str,
        lamport_timestamp: int,
        request_number: int,
    ) -> printing_pb2.PrintRequest:
        """
        Build PrintRequest message.
        
        Args:
            client_id: Client identifier
            message_content: Content to print
            lamport_timestamp: Current Lamport timestamp
            request_number: Request sequence number
            
        Returns:
            PrintRequest protobuf message
        """
        return printing_pb2.PrintRequest(
            client_id=client_id,
            message_content=message_content,
            lamport_timestamp=lamport_timestamp,
            request_number=request_number,
        )

    @staticmethod
    def build_print_response(
        success: bool,
        confirmation_message: str,
        lamport_timestamp: int,
    ) -> printing_pb2.PrintResponse:
        """
        Build PrintResponse message.
        
        Args:
            success: Whether print was successful
            confirmation_message: Confirmation message
            lamport_timestamp: Current Lamport timestamp
            
        Returns:
            PrintResponse protobuf message
        """
        return printing_pb2.PrintResponse(
            success=success,
            confirmation_message=confirmation_message,
            lamport_timestamp=lamport_timestamp,
        )

    @staticmethod
    def build_access_request(
        client_id: int,
        lamport_timestamp: int,
        request_number: int,
    ) -> printing_pb2.AccessRequest:
        """
        Build AccessRequest message for mutual exclusion.
        
        Args:
            client_id: Client identifier
            lamport_timestamp: Current Lamport timestamp
            request_number: Request sequence number
            
        Returns:
            AccessRequest protobuf message
        """
        return printing_pb2.AccessRequest(
            client_id=client_id,
            lamport_timestamp=lamport_timestamp,
            request_number=request_number,
        )

    @staticmethod
    def build_access_response(
        access_granted: bool,
        lamport_timestamp: int,
    ) -> printing_pb2.AccessResponse:
        """
        Build AccessResponse message.
        
        Args:
            access_granted: Whether access is granted
            lamport_timestamp: Current Lamport timestamp
            
        Returns:
            AccessResponse protobuf message
        """
        return printing_pb2.AccessResponse(
            access_granted=access_granted,
            lamport_timestamp=lamport_timestamp,
        )

    @staticmethod
    def build_access_release(
        client_id: int,
        lamport_timestamp: int,
        request_number: int,
    ) -> printing_pb2.AccessRelease:
        """
        Build AccessRelease message.
        
        Args:
            client_id: Client identifier
            lamport_timestamp: Current Lamport timestamp
            request_number: Request sequence number being released
            
        Returns:
            AccessRelease protobuf message
        """
        return printing_pb2.AccessRelease(
            client_id=client_id,
            lamport_timestamp=lamport_timestamp,
            request_number=request_number,
        )

    @staticmethod
    def build_empty() -> printing_pb2.Empty:
        """
        Build Empty message.
        
        Returns:
            Empty protobuf message
        """
        return printing_pb2.Empty()

