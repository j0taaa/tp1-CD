#!/bin/bash

# Manual test script for concurrent access ordering
# This script launches 1 server + 3 clients and verifies correct ordering

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Manual Test: Concurrent Access Ordering"
echo "==========================================${NC}"
echo ""
echo "This test will:"
echo "  1. Start printer server on port 50051"
echo "  2. Start 3 clients on ports 50052, 50053, 50054"
echo "  3. Verify mutual exclusion and timestamp ordering"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all processes${NC}"
echo ""

# Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run 'python3 -m venv venv' first."
        exit 1
    fi
fi

# Create log directory
LOG_DIR="$PROJECT_ROOT/test_logs"
mkdir -p "$LOG_DIR"

# Start server in background
echo -e "${GREEN}Starting printer server...${NC}"
PYTHONPATH="$PROJECT_ROOT" python3 printer/server.py \
    --port 50051 \
    --delay-min 2.0 \
    --delay-max 3.0 > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
sleep 2

# Start clients
echo -e "${GREEN}Starting clients...${NC}"

# Client 1
PYTHONPATH="$PROJECT_ROOT" python3 client/main.py \
    --id 1 \
    --server localhost:50051 \
    --port 50052 \
    --clients localhost:50053,localhost:50054 \
    --job-interval-min 3.0 \
    --job-interval-max 5.0 > "$LOG_DIR/client1.log" 2>&1 &
CLIENT1_PID=$!

sleep 1

# Client 2
PYTHONPATH="$PROJECT_ROOT" python3 client/main.py \
    --id 2 \
    --server localhost:50051 \
    --port 50053 \
    --clients localhost:50052,localhost:50054 \
    --job-interval-min 3.0 \
    --job-interval-max 5.0 > "$LOG_DIR/client2.log" 2>&1 &
CLIENT2_PID=$!

sleep 1

# Client 3
PYTHONPATH="$PROJECT_ROOT" python3 client/main.py \
    --id 3 \
    --server localhost:50051 \
    --port 50054 \
    --clients localhost:50052,localhost:50053 \
    --job-interval-min 3.0 \
    --job-interval-max 5.0 > "$LOG_DIR/client3.log" 2>&1 &
CLIENT3_PID=$!

echo "Client PIDs: $CLIENT1_PID, $CLIENT2_PID, $CLIENT3_PID"
echo ""
echo -e "${BLUE}All processes started. Monitor logs in $LOG_DIR${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all processes...${NC}"
    kill $SERVER_PID $CLIENT1_PID $CLIENT2_PID $CLIENT3_PID 2>/dev/null || true
    wait $SERVER_PID $CLIENT1_PID $CLIENT2_PID $CLIENT3_PID 2>/dev/null || true
    echo -e "${GREEN}Stopped. Logs available in $LOG_DIR${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait

