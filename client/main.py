"""
Client Node Architecture

Intelligent client that implements Ricart-Agrawala mutual exclusion algorithm.
Acts as both gRPC server (for MutualExclusionService) and gRPC client (for printer and peers).
"""

import argparse
import threading
import time
import random
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import grpc
from concurrent import futures
import printing_pb2
import printing_pb2_grpc
from common.lamport_clock import LamportClock
from common.logger import create_client_logger
from common.message_builder import MessageBuilder


@dataclass
class PendingRequest:
    """Represents a pending access request."""
    client_id: int
    lamport_timestamp: int
    request_number: int


@dataclass
class MutualExclusionServiceServicer(printing_pb2_grpc.MutualExclusionServiceServicer):
    """
    Implementation of MutualExclusionService for receiving requests from peers.
    
    This will be implemented with Ricart-Agrawala logic in step 7.
    """
    
    def __init__(self, client_node):
        """
        Initialize the servicer.
        
        Args:
            client_node: Reference to the ClientNode instance
        """
        self.client_node = client_node
    
    def RequestAccess(self, request: printing_pb2.AccessRequest, context):
        """
        Handle access request from peer (Ricart-Agrawala algorithm).
        
        Reference: Ricart, Glenn, and Ashok K. Agrawala. 
        "An optimal algorithm for mutual exclusion in computer networks." 
        Communications of the ACM 24.1 (1981): 9-17.
        
        Algorithm decision logic:
        1. If not in CS and not waiting for CS -> reply immediately (grant access)
        2. If in CS -> defer reply (add to deferred_replies)
        3. If waiting for CS:
           - Compare timestamps: if incoming TS < own TS, reply immediately
           - If incoming TS > own TS, defer reply
           - If TS equal, compare client IDs (lower ID wins)
        
        Args:
            request: AccessRequest from peer
            context: gRPC context
            
        Returns:
            AccessResponse indicating if access is granted
        """
        client_node = self.client_node
        
        # Update clock with received timestamp (Lamport rule: on receive)
        response_timestamp = client_node.clock.receive_event(request.lamport_timestamp)
        
        with client_node.lock:
            should_defer, log_message = client_node._evaluate_access_request(request)

            if should_defer:
                # Only add to deferred_replies if not already there
                if request.client_id not in client_node.deferred_replies:
                    client_node.deferred_replies[request.client_id] = request
                    client_node.logger.info(
                        log_message,
                        lamport_timestamp=response_timestamp
                    )
                
                # Return negative response when deferring
                return MessageBuilder.build_access_response(
                    access_granted=False,
                    lamport_timestamp=client_node.clock.tick()
                )

            # Grant access immediately
            client_node.logger.info(
                log_message,
                lamport_timestamp=client_node.clock.get_time()
            )
            
            response_timestamp = client_node.clock.tick()
            return MessageBuilder.build_access_response(
                access_granted=True,
                lamport_timestamp=response_timestamp,
            )
    
    def ReleaseAccess(self, request: printing_pb2.AccessRelease, context):
        """
        Handle access release from peer (Ricart-Agrawala algorithm).
        
        When a peer releases access, we need to:
        1. Update our clock
        2. Process any deferred replies (if we're waiting for access)
        
        Args:
            request: AccessRelease from peer
            context: gRPC context
            
        Returns:
            Empty response
        """
        client_node = self.client_node
        
        # Update clock with received timestamp
        timestamp = client_node.clock.receive_event(request.lamport_timestamp)
        
        client_node.logger.info(
            f"AccessRelease recebido de cliente {request.client_id} (TS: {request.lamport_timestamp})",
            lamport_timestamp=timestamp
        )
        
        # Note: The actual processing of deferred replies happens when we receive
        # the release while waiting. The peer who released will have already
        # sent replies to all deferred requests when they exited CS.
        # This method just acknowledges receipt.
        
        return MessageBuilder.build_empty()


class ClientNode:
    """
    Client node implementing distributed mutual exclusion.
    
    Each client acts as:
    - gRPC server: Receives MutualExclusionService requests from peers
    - gRPC client: Sends requests to printer server and peer clients
    """
    
    def __init__(
        self,
        client_id: int,
        port: int,
        printer_server: str,
        peer_addresses: List[str],
        job_interval_min: float = 5.0,
        job_interval_max: float = 10.0,
    ):
        """
        Initialize client node.
        
        Args:
            client_id: Unique client identifier
            port: Port for this client's gRPC server
            printer_server: Address of printer server (e.g., "localhost:50051")
            peer_addresses: List of peer client addresses (e.g., ["localhost:50053", "localhost:50054"])
            job_interval_min: Minimum interval between print jobs in seconds (default: 5.0)
            job_interval_max: Maximum interval between print jobs in seconds (default: 10.0)
        """
        self.client_id = client_id
        self.port = port
        self.printer_server = printer_server
        self.peer_addresses = peer_addresses
        self.job_interval_min = job_interval_min
        self.job_interval_max = job_interval_max
        self.job_counter = 0  # Counter for generating unique job messages
        
        # Utilities
        self.clock = LamportClock()
        self.logger = create_client_logger(client_id)
        
        # Internal state
        self.request_number = 0  # Sequence number for requests
        self.request_queue: deque = deque()  # Queue of pending requests

        # State tracking
        self.has_access = False  # Whether we currently have access to the resource
        self.waiting_for_access = False  # Whether we are waiting for access (in request queue)
        self.deferred_replies: Dict[int, printing_pb2.AccessRequest] = {}
        self.received_replies: Set[str] = set()  # Track which peers have replied
        self.outstanding_replies: Set[str] = set()  # Peers dos quais aguardamos resposta
        
        # Threading (must be initialized before access_condition)
        self.lock = threading.Lock()
        self.running = False
        self.access_condition = threading.Condition(self.lock)  # Condition variable for waiting for access
        self.defer_condition = threading.Condition(self.lock)  # Condition variable for deferred replies

        # gRPC components
        self.grpc_server = None
        self.printer_stub = None
        self.peer_stubs: Dict[str, printing_pb2_grpc.MutualExclusionServiceStub] = {}

    def _evaluate_access_request(self, request: printing_pb2.AccessRequest) -> Tuple[bool, str]:
        """Evaluate whether an incoming request should be deferred or granted."""

        if self.has_access:
            # Always defer if we're in critical section
            return True, (
                f"AccessRequest de cliente {request.client_id} DEFERIDO (em CS, TS: {request.lamport_timestamp})"
            )

        if self.waiting_for_access and self.request_queue:
            # Make sure request queue is sorted
            self.request_queue = deque(sorted(
                self.request_queue,
                key=lambda x: (x.lamport_timestamp, x.client_id)
            ))
            
            our_request = self.request_queue[0]
            our_timestamp = our_request.lamport_timestamp

            # Compare timestamps first
            if request.lamport_timestamp < our_timestamp:
                return False, (
                    f"AccessRequest de cliente {request.client_id} CONCEDIDO "
                    f"(TS {request.lamport_timestamp} < nosso TS {our_timestamp})"
                )

            if request.lamport_timestamp > our_timestamp:
                return True, (
                    f"AccessRequest de cliente {request.client_id} DEFERIDO "
                    f"(TS {request.lamport_timestamp} > nosso TS {our_timestamp})"
                )

            # Break timestamp ties with client IDs
            if request.client_id < self.client_id:
                return False, (
                    f"AccessRequest de cliente {request.client_id} CONCEDIDO "
                    f"(TS igual, ID {request.client_id} < nosso ID {self.client_id})"
                )

            return True, (
                f"AccessRequest de cliente {request.client_id} DEFERIDO "
                f"(TS igual, ID {request.client_id} >= nosso ID {self.client_id})"
            )

        # Not in CS and not waiting -> grant immediately
        return False, (
            f"AccessRequest de cliente {request.client_id} CONCEDIDO (não em CS)"
        )
    
    def initialize_grpc(self):
        """Initialize gRPC server and client stubs."""
        # Create gRPC server
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Add MutualExclusionService servicer
        servicer = MutualExclusionServiceServicer(self)
        printing_pb2_grpc.add_MutualExclusionServiceServicer_to_server(servicer, self.grpc_server)
        
        # Listen on port
        listen_addr = f'[::]:{self.port}'
        self.grpc_server.add_insecure_port(listen_addr)
        
        # Create printer client stub
        printer_channel = grpc.insecure_channel(self.printer_server)
        self.printer_stub = printing_pb2_grpc.PrintingServiceStub(printer_channel)
        
        # Create peer client stubs
        for peer_addr in self.peer_addresses:
            peer_channel = grpc.insecure_channel(peer_addr)
            self.peer_stubs[peer_addr] = printing_pb2_grpc.MutualExclusionServiceStub(peer_channel)
        
        self.logger.info(f"gRPC inicializado - Servidor na porta {self.port}")
        self.logger.info(f"Conectado ao servidor de impressão: {self.printer_server}")
        self.logger.info(f"Conectado a {len(self.peer_addresses)} peer(s)")
    
    def start(self):
        """Start the client node."""
        self.initialize_grpc()
        self.grpc_server.start()
        self.running = True
        
        self.logger.info(
            f"Cliente {self.client_id} iniciado na porta {self.port}",
            lamport_timestamp=self.clock.get_time()
        )
        
        # Start status reporting thread
        status_thread = threading.Thread(target=self._status_reporter, daemon=True)
        status_thread.start()
        
        # Start automatic job generation thread
        job_thread = threading.Thread(target=self._automatic_job_generator, daemon=True)
        job_thread.start()
        
        try:
            self.grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            self.logger.info("Cliente sendo encerrado...")
            self.stop()
    
    def stop(self):
        """Stop the client node."""
        self.running = False
        if self.grpc_server:
            self.grpc_server.stop(grace=5)
    
    def _status_reporter(self):
        """Periodically report client status."""
        while self.running:
            time.sleep(5)  # Report every 5 seconds
            if not self.running:
                break
            
            with self.lock:
                queue_size = len(self.request_queue)
                outstanding_count = len(self.outstanding_replies)
                has_access = self.has_access
                clock_time = self.clock.get_time()
            
            self.logger.info(
                f"Status - Clock: {clock_time}, "
                f"Fila: {queue_size}, "
                f"Aguardando respostas: {outstanding_count}, "
                f"Tem acesso: {has_access}",
                lamport_timestamp=clock_time
            )
    
    def request_print_access(self):
        """
        Request access to print using Ricart-Agrawala algorithm.
        
        Algorithm steps:
        1. Increment clock (Lamport rule: before send)
        2. Broadcast AccessRequest to all peers
        3. Wait for replies from all peers
        4. When all replies received, grant access
        
        Reference: Ricart, Glenn, and Ashok K. Agrawala.
        "An optimal algorithm for mutual exclusion in computer networks."
        Communications of the ACM 24.1 (1981): 9-17.
        """
        with self.lock:
            self.request_number += 1
            timestamp = self.clock.send_event()
            
            self.logger.info(
                f"Solicitando acesso para impressão (requisição #{self.request_number}, TS: {timestamp})",
                lamport_timestamp=timestamp
            )
            
            # Create pending request
            pending = PendingRequest(
                client_id=self.client_id,
                lamport_timestamp=timestamp,
                request_number=self.request_number
            )
            self.request_queue.append(pending)
            self.waiting_for_access = True
            self.received_replies.clear()
            self.outstanding_replies = set(self.peer_addresses)
        
        # Broadcast AccessRequest to all peers
        self._broadcast_access_request(pending)
        
        # Wait for all replies
        with self.access_condition:
            while len(self.received_replies) < len(self.peer_addresses):
                self.logger.info(
                    f"Aguardando respostas ({len(self.received_replies)}/{len(self.peer_addresses)})",
                    lamport_timestamp=self.clock.get_time()
                )
                self.access_condition.wait(timeout=1.0)
        
        # All replies received - grant access
        with self.lock:
            self.has_access = True
            self.waiting_for_access = False
            
            self.logger.info(
                f"Acesso concedido! Todas as respostas recebidas.",
                lamport_timestamp=self.clock.get_time()
            )
    
    def _broadcast_access_request(self, pending_request: PendingRequest):
        """
        Broadcast AccessRequest to all peer clients.
        
        Args:
            pending_request: The pending request to broadcast
        """
        request = MessageBuilder.build_access_request(
            client_id=self.client_id,
            lamport_timestamp=pending_request.lamport_timestamp,
            request_number=pending_request.request_number,
        )
        
        # Send to all peers asynchronously
        for peer_addr in self.peer_addresses:
            threading.Thread(
                target=self._send_access_request_to_peer,
                args=(peer_addr, request),
                daemon=True
            ).start()
    
    def _send_access_request_to_peer(self, peer_addr: str, request: printing_pb2.AccessRequest):
        """
        Send AccessRequest to a specific peer and handle response.
        
        Args:
            peer_addr: Address of the peer
            request: AccessRequest message
        """
        try:
            stub = self.peer_stubs[peer_addr]
            response = stub.RequestAccess(request)
            
            # Update clock with response timestamp
            with self.lock:
                self.clock.receive_event(response.lamport_timestamp)
            
            # Record that we received a reply
            with self.access_condition:
                self.outstanding_replies.discard(peer_addr)
                self.received_replies.add(peer_addr)
                self.logger.info(
                    f"Resposta recebida de {peer_addr} (granted: {response.access_granted})",
                    lamport_timestamp=self.clock.get_time()
                )
                self.access_condition.notify_all()
        
        except grpc.RpcError as e:
            self.logger.error(
                f"Erro ao enviar AccessRequest para {peer_addr}: {e.code()}",
                lamport_timestamp=self.clock.get_time()
            )
            # Still count as received to avoid deadlock (in real system, might retry)
            with self.access_condition:
                self.outstanding_replies.discard(peer_addr)
                self.received_replies.add(peer_addr)
                self.access_condition.notify_all()
    
    def release_access(self):
        """
        Release access and process deferred replies (Ricart-Agrawala algorithm).
        
        When exiting CS:
        1. Broadcast ReleaseAccess to all deferred peers
        2. Clear access state
        """
        with self.lock:
            if not self.has_access:
                self.logger.warning(
                    "Tentativa de liberar acesso sem ter acesso",
                    lamport_timestamp=self.clock.get_time()
                )
                return
            
            # Increment clock for release
            timestamp = self.clock.send_event()
            
            self.logger.info(
                f"Liberando acesso e processando {len(self.deferred_replies)} resposta(s) deferida(s)",
                lamport_timestamp=timestamp
            )
            
            # Process all deferred replies before releasing
            deferred_requests = list(self.deferred_replies.values())
            self.deferred_replies.clear()

            # Create release message
            release_msg = MessageBuilder.build_access_release(
                client_id=self.client_id,
                lamport_timestamp=timestamp,
                request_number=self.request_number,
            )
            
            # Clear access state
            self.has_access = False
            
            # Remove our request from queue
            if len(self.request_queue) > 0:
                self.request_queue.popleft()
            
            # Send releases to all peers first
            for peer_addr in self.peer_addresses:
                threading.Thread(
                    target=self._send_access_release_to_peer,
                    args=(peer_addr, release_msg),
                    daemon=True
                ).start()

            # Now process all deferred requests in order of timestamp
            deferred_requests.sort(key=lambda x: (x.lamport_timestamp, x.client_id))
            for peer_id, request in self.deferred_replies.items():
                # Find the peer address based on client ID
                peer_addr = None
                for addr in self.peer_stubs:
                    if f"cliente {peer_id}" in addr:  # matches format like "localhost:50052"
                        peer_addr = addr
                        break
                
                if not peer_addr:
                    self.logger.error(
                        f"Não foi possível encontrar o endereço do cliente {peer_id}",
                        lamport_timestamp=self.clock.get_time()
                    )
                    continue

                response = MessageBuilder.build_access_response(
                    access_granted=True,
                    lamport_timestamp=self.clock.tick()
                )
                try:
                    self.peer_stubs[peer_addr].ReplyToAccessRequest(response)
                    self.logger.info(
                        f"Enviando resposta adiada para cliente {peer_id} em {peer_addr}",
                        lamport_timestamp=self.clock.get_time()
                    )
                except grpc.RpcError as e:
                    self.logger.error(
                        f"Erro ao enviar resposta adiada para cliente {peer_id}: {e.code()}",
                        lamport_timestamp=self.clock.get_time()
                    )

            # Clear tracking state
            self.outstanding_replies.clear()
    
    def _send_access_release_to_peer(self, peer_addr: str, release: printing_pb2.AccessRelease):
        """
        Send AccessRelease to a specific peer.
        
        Args:
            peer_addr: Address of the peer
            release: AccessRelease message
        """
        try:
            stub = self.peer_stubs[peer_addr]
            stub.ReleaseAccess(release)
            
            self.logger.info(
                f"AccessRelease enviado para {peer_addr}",
                lamport_timestamp=self.clock.get_time()
            )
        
        except grpc.RpcError as e:
            self.logger.error(
                f"Erro ao enviar AccessRelease para {peer_addr}: {e.code()}",
                lamport_timestamp=self.clock.get_time()
            )
    
    
    def print_document(self, message_content: str, max_retries: int = 3):
        """
        Send document to printer with retry logic.
        
        This method should be called AFTER obtaining mutual exclusion access.
        It handles retries and error recovery.
        
        Args:
            message_content: Content to print
            max_retries: Maximum number of retry attempts (default: 3)
        """
        timestamp = self.clock.send_event()
        
        request = MessageBuilder.build_print_request(
            client_id=self.client_id,
            message_content=message_content,
            lamport_timestamp=timestamp,
            request_number=self.request_number,
        )
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.logger.info(
                    f"Enviando documento para impressão: {message_content}",
                    lamport_timestamp=self.clock.get_time()
                )
                
                # Set timeout for RPC call (10 seconds)
                response = self.printer_stub.SendToPrinter(
                    request,
                    timeout=10.0
                )
                
                # Update clock with server's response timestamp
                self.clock.receive_event(response.lamport_timestamp)
                
                if response.success:
                    self.logger.info(
                        f"Impressão confirmada: {response.confirmation_message}",
                        lamport_timestamp=self.clock.get_time()
                    )
                    return True  # Success
                else:
                    self.logger.error(
                        "Falha na impressão - servidor retornou sucesso=False",
                        lamport_timestamp=self.clock.get_time()
                    )
                    return False
                
            except grpc.RpcError as e:
                retry_count += 1
                error_code = e.code()
                
                # Update clock for error event
                self.clock.tick()
                
                if retry_count < max_retries:
                    # Retryable errors
                    if error_code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED, grpc.StatusCode.RESOURCE_EXHAUSTED):
                        wait_time = min(2 ** retry_count, 10)  # Exponential backoff, max 10s
                        self.logger.warning(
                            f"Erro ao comunicar com servidor ({error_code.name}), "
                            f"tentando novamente em {wait_time}s (tentativa {retry_count}/{max_retries})",
                            lamport_timestamp=self.clock.get_time()
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        # Non-retryable errors
                        self.logger.error(
                            f"Erro não recuperável ao comunicar com servidor: {error_code.name}",
                            lamport_timestamp=self.clock.get_time()
                        )
                        return False
                else:
                    # Max retries reached
                    self.logger.error(
                        f"Falha ao comunicar com servidor após {max_retries} tentativas: {error_code.name}",
                        lamport_timestamp=self.clock.get_time()
                    )
                    return False
            
            except Exception as e:
                retry_count += 1
                self.clock.tick()
                self.logger.error(
                    f"Erro inesperado ao imprimir: {type(e).__name__}: {str(e)}",
                    lamport_timestamp=self.clock.get_time()
                )
                if retry_count >= max_retries:
                    return False
                time.sleep(1)  # Brief wait before retry
        
        return False  # Failed after all retries
    
    def execute_print_job(self, message_content: str):
        """
        Complete printing workflow with mutual exclusion.
        
        This method:
        1. Requests access using Ricart-Agrawala algorithm
        2. Prints document (with retry logic)
        3. Releases access
        
        Args:
            message_content: Content to print
        """
        try:
            # Step 1: Request access
            self.logger.info(
                f"Iniciando workflow de impressão: {message_content}",
                lamport_timestamp=self.clock.get_time()
            )
            
            self.request_print_access()
            
            # Step 2: Print document (only if we have access)
            if self.has_access:
                success = self.print_document(message_content)
                
                if success:
                    self.logger.info(
                        "Job de impressão concluído com sucesso",
                        lamport_timestamp=self.clock.get_time()
                    )
                else:
                    self.logger.error(
                        "Job de impressão falhou",
                        lamport_timestamp=self.clock.get_time()
                    )
            else:
                self.logger.error(
                    "Acesso não concedido - não é possível imprimir",
                    lamport_timestamp=self.clock.get_time()
                )
            
            # Step 3: Release access (always release, even if print failed)
            self.release_access()
            
        except Exception as e:
            self.logger.error(
                f"Erro no workflow de impressão: {type(e).__name__}: {str(e)}",
                lamport_timestamp=self.clock.get_time()
            )
            # Always try to release access if we had it
            with self.lock:
                if self.has_access:
                    self.release_access()
    
    def _automatic_job_generator(self):
        """
        Generate print jobs automatically at random intervals.
        
        This thread runs continuously, generating print jobs based on
        the configured interval range.
        """
        while self.running:
            # Wait for random interval before generating next job
            interval = random.uniform(self.job_interval_min, self.job_interval_max)
            
            # Wait in smaller chunks to allow for graceful shutdown
            waited = 0.0
            while waited < interval and self.running:
                time.sleep(min(0.5, interval - waited))
                waited += 0.5
            
            if not self.running:
                break
            
            # Generate unique job message
            self.job_counter += 1
            message_content = f"Documento #{self.job_counter} do cliente {self.client_id}"
            
            # Execute print job in a separate thread to avoid blocking
            threading.Thread(
                target=self.execute_print_job,
                args=(message_content,),
                daemon=True
            ).start()


def parse_peer_addresses(peers_str: str) -> List[str]:
    """
    Parse comma-separated peer addresses.
    
    Args:
        peers_str: Comma-separated list of addresses (e.g., "localhost:50053,localhost:50054")
        
    Returns:
        List of peer addresses
    """
    if not peers_str:
        return []
    return [addr.strip() for addr in peers_str.split(',') if addr.strip()]


def main():
    """Main entry point for the client."""
    parser = argparse.ArgumentParser(
        description='Cliente Inteligente - Sistema de Impressão Distribuída',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplo de uso:
  python3 client/main.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
        """
    )
    
    parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID único do cliente'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        required=True,
        help='Porta para o servidor gRPC do cliente'
    )
    
    parser.add_argument(
        '--server',
        type=str,
        required=True,
        help='Endereço do servidor de impressão (ex: localhost:50051)'
    )
    
    parser.add_argument(
        '--clients',
        type=str,
        default='',
        help='Lista de endereços de outros clientes separados por vírgula (ex: localhost:50053,localhost:50054)'
    )
    
    parser.add_argument(
        '--job-interval-min',
        type=float,
        default=5.0,
        help='Intervalo mínimo entre jobs de impressão em segundos (padrão: 5.0)'
    )
    
    parser.add_argument(
        '--job-interval-max',
        type=float,
        default=10.0,
        help='Intervalo máximo entre jobs de impressão em segundos (padrão: 10.0)'
    )
    
    args = parser.parse_args()
    
    # Validate interval arguments
    if args.job_interval_min < 0 or args.job_interval_max < 0:
        print("Erro: Intervalos de job devem ser valores positivos")
        return
    
    if args.job_interval_min > args.job_interval_max:
        print("Erro: job-interval-min deve ser menor ou igual a job-interval-max")
        return
    
    # Parse peer addresses
    peer_addresses = parse_peer_addresses(args.clients)
    
    # Create and start client node
    client = ClientNode(
        client_id=args.id,
        port=args.port,
        printer_server=args.server,
        peer_addresses=peer_addresses,
        job_interval_min=args.job_interval_min,
        job_interval_max=args.job_interval_max,
    )
    
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()


if __name__ == '__main__':
    main()

