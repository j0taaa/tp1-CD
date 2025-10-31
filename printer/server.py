"""
Printer Server ("Burro")

Simple gRPC server that receives print requests and prints them.
Does NOT participate in mutual exclusion algorithm.
"""

import argparse
import time
import random
import grpc
from concurrent import futures
import printing_pb2
import printing_pb2_grpc
from common.logger import create_server_logger
from common.message_builder import MessageBuilder
from common.lamport_clock import LamportClock


class PrintingServiceServicer(printing_pb2_grpc.PrintingServiceServicer):
    """
    Implementation of the PrintingService.
    
    This is a "dumb" server that just prints messages and returns confirmations.
    It does NOT participate in mutual exclusion.
    """

    def __init__(self, print_delay_min: float = 2.0, print_delay_max: float = 3.0):
        """
        Initialize the printing service.
        
        Args:
            print_delay_min: Minimum delay in seconds (default: 2.0)
            print_delay_max: Maximum delay in seconds (default: 3.0)
        """
        self.logger = create_server_logger()
        self.print_delay_min = print_delay_min
        self.print_delay_max = print_delay_max
        
        # Server maintains its own Lamport clock for responses
        # It updates based on received timestamps
        self.clock = LamportClock()

    def SendToPrinter(self, request: printing_pb2.PrintRequest, context):
        """
        Handle print request from client.
        
        This method:
        1. Updates server's Lamport clock with received timestamp
        2. Prints the message in the specified format
        3. Simulates printing delay
        4. Returns confirmation with updated timestamp
        
        Args:
            request: PrintRequest containing client_id, message, timestamp, etc.
            context: gRPC context
            
        Returns:
            PrintResponse with success status and confirmation message
        """
        # Update server clock with received timestamp
        server_timestamp = self.clock.receive_event(request.lamport_timestamp)
        
        # Log the print request in the specified format
        # Format: [TS: {timestamp}] CLIENTE {id}: {mensagem}
        # We need to print as if coming from the client, not the server
        print(f"[TS: {request.lamport_timestamp}] CLIENTE {request.client_id}: {request.message_content}", flush=True)
        
        # Simulate printing delay (2-3 seconds)
        delay = random.uniform(self.print_delay_min, self.print_delay_max)
        time.sleep(delay)
        
        # Increment clock for the response
        response_timestamp = self.clock.tick()
        
        # Create and return confirmation response
        response = MessageBuilder.build_print_response(
            success=True,
            confirmation_message=f"Documento do cliente {request.client_id} impresso com sucesso",
            lamport_timestamp=response_timestamp,
        )
        
        self.logger.info(
            f"Confirmação enviada para cliente {request.client_id}",
            lamport_timestamp=response_timestamp
        )
        
        return response


def serve(port: int = 50051, print_delay_min: float = 2.0, print_delay_max: float = 3.0):
    """
    Start the gRPC server.
    
    Args:
        port: Port to listen on (default: 50051)
        print_delay_min: Minimum print delay in seconds (default: 2.0)
        print_delay_max: Maximum print delay in seconds (default: 3.0)
    """
    logger = create_server_logger()
    
    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add servicer
    printing_servicer = PrintingServiceServicer(print_delay_min, print_delay_max)
    printing_pb2_grpc.add_PrintingServiceServicer_to_server(printing_servicer, server)
    
    # Listen on port
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    # Start server
    server.start()
    logger.info(f"Servidor de impressão iniciado na porta {port}")
    logger.info(f"Delay de impressão: {print_delay_min}-{print_delay_max} segundos")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Servidor sendo encerrado...")
        server.stop(grace=5)


def main():
    """Main entry point for the printer server."""
    parser = argparse.ArgumentParser(
        description='Servidor de Impressão Distribuída (Burro)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplo de uso:
  python3 printer/server.py --port 50051 --delay-min 2.0 --delay-max 3.0
        """
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=50051,
        help='Porta para o servidor escutar (padrão: 50051)'
    )
    
    parser.add_argument(
        '--delay-min',
        type=float,
        default=2.0,
        help='Delay mínimo de impressão em segundos (padrão: 2.0)'
    )
    
    parser.add_argument(
        '--delay-max',
        type=float,
        default=3.0,
        help='Delay máximo de impressão em segundos (padrão: 3.0)'
    )
    
    args = parser.parse_args()
    
    # Validate delay arguments
    if args.delay_min < 0 or args.delay_max < 0:
        print("Erro: Delays devem ser valores positivos")
        return
    
    if args.delay_min > args.delay_max:
        print("Erro: delay-min deve ser menor ou igual a delay-max")
        return
    
    serve(port=args.port, print_delay_min=args.delay_min, print_delay_max=args.delay_max)


if __name__ == '__main__':
    main()

