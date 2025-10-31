# Testing Strategy

## Overview

This document describes the comprehensive testing strategy for the Distributed Printing System with Ricart-Agrawala mutual exclusion.

## Test Structure

### Unit Tests (`tests/unit/`)

#### 1. Lamport Clock Tests (`test_lamport_clock.py`)
- ✅ Initialization
- ✅ Tick operations
- ✅ Send/receive events
- ✅ Thread safety
- ✅ Manual updates
- ✅ String representation

**Coverage:** Core Lamport clock functionality

#### 2. Logger Tests (`test_logger.py`)
- ✅ Client logger formatting
- ✅ Server logger formatting
- ✅ Log levels (info, warning, error, debug)
- ✅ Print request formatting
- ✅ Factory functions

**Coverage:** Logging utilities and message formatting

#### 3. Message Builder Tests (`test_message_builder.py`)
- ✅ PrintRequest building
- ✅ PrintResponse building
- ✅ AccessRequest building
- ✅ AccessResponse building
- ✅ AccessRelease building
- ✅ Empty message building

**Coverage:** gRPC message construction

#### 4. Printer Server Tests (`test_printer_server.py`)
- ✅ Server initialization
- ✅ Custom delay configuration
- ✅ Clock updates on requests
- ✅ Response format validation
- ✅ Delay simulation
- ✅ Message logging
- ✅ Multiple requests clock progression

**Coverage:** Printer server functionality

#### 5. Client Node Tests (`test_client_node.py`)
- ✅ Client initialization
- ✅ Peer address parsing
- ✅ Print access requests
- ✅ Clock updates
- ✅ gRPC initialization
- ✅ Status reporter thread
- ✅ Servicer initialization
- ✅ RequestAccess clock updates
- ✅ ReleaseAccess clock updates

**Coverage:** Client node architecture and basic operations

### Integration Tests (`tests/integration/`)

#### 1. Ricart-Agrawala Integration Tests (`test_ricart_agrawala.py`)
- ✅ Two clients mutual exclusion
- ✅ Timestamp comparison logic
- ✅ Lamport clock monotonicity
- ✅ Concurrent access requests

**Coverage:** Full algorithm flow with multiple clients

#### 2. Timestamp Monotonicity Tests (`test_timestamp_monotonicity.py`)
- ✅ Basic Lamport clock monotonicity
- ✅ Thread safety monotonicity
- ✅ Client timestamp monotonicity
- ✅ Request/response cycle monotonicity

**Coverage:** Timestamp ordering verification

## Test Execution

### Run All Tests
```bash
# From project root
source venv/bin/activate
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -v
```

### Run Specific Test Suite
```bash
pytest tests/unit/test_lamport_clock.py -v
pytest tests/integration/test_ricart_agrawala.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Manual Testing

### Scripts

#### 1. Run Printer Server
```bash
./scripts/run_server.sh [--port PORT] [--delay-min MIN] [--delay-max MAX]
```

Example:
```bash
./scripts/run_server.sh --port 50051 --delay-min 2.0 --delay-max 3.0
```

#### 2. Run Client
```bash
./scripts/run_client.sh --id ID --port PORT --server SERVER [--clients CLIENTS] [--job-interval-min MIN] [--job-interval-max MAX]
```

Example:
```bash
./scripts/run_client.sh --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
```

#### 3. Run Full Manual Test (3 clients)
```bash
./scripts/run_manual_test.sh
```

This script:
- Starts printer server on port 50051
- Starts 3 clients on ports 50052, 50053, 50054
- Monitors concurrent access ordering
- Logs output to `test_logs/` directory

### Manual Test Scenarios

#### Scenario 1: Basic Functionality
1. Start printer server
2. Start client 1
3. Verify client can request access and print
4. Verify access is released after printing

#### Scenario 2: Concurrent Access (2 clients)
1. Start printer server
2. Start client 1
3. Start client 2
4. Observe:
   - Only one client has access at a time
   - Access requests are properly queued
   - Timestamps determine access order

#### Scenario 3: Concurrent Access (3 clients)
1. Start printer server
2. Start clients 1, 2, 3 simultaneously
3. Observe:
   - Mutual exclusion maintained
   - Timestamp-based ordering
   - Proper release/re-acquisition

## Verification Criteria

### Timestamp Monotonicity
- ✅ All Lamport timestamps increase monotonically
- ✅ No timestamp decreases
- ✅ Thread-safe timestamp updates

### Mutual Exclusion
- ✅ Only one client has access at a time
- ✅ Access requests are properly queued
- ✅ Releases trigger next client's access

### Ricart-Agrawala Correctness
- ✅ Lower timestamps get priority
- ✅ Client ID used as tiebreaker
- ✅ Deferred replies processed correctly

### Error Handling
- ✅ RPC errors handled gracefully
- ✅ Retries work correctly
- ✅ Access always released, even on errors

## Test Results

### Current Status
- ✅ **34 unit tests** - All passing
- ✅ **8 integration tests** - All passing
- ✅ **Total: 42 tests** - 100% passing

### Coverage Areas
- Lamport clock implementation: ✅
- Logger utilities: ✅
- Message building: ✅
- Printer server: ✅
- Client node architecture: ✅
- Ricart-Agrawala algorithm: ✅
- Timestamp monotonicity: ✅
- Error handling: ✅

## Running Tests in CI/CD

Tests can be run in continuous integration environments:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --tb=short

# Check for linting errors
ruff check .
```

## Notes

- Integration tests use ephemeral ports to avoid conflicts
- Manual tests use fixed ports (50051-50054) for consistency
- All tests are deterministic and repeatable
- Tests clean up resources properly

