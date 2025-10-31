#!/bin/bash

# Script to run printer server for manual testing
# Usage: ./scripts/run_server.sh [--port PORT] [--delay-min MIN] [--delay-max MAX]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Default values
PORT=50051
DELAY_MIN=2.0
DELAY_MAX=3.0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --delay-min)
            DELAY_MIN="$2"
            shift 2
            ;;
        --delay-max)
            DELAY_MAX="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--port PORT] [--delay-min MIN] [--delay-max MAX]"
            exit 1
            ;;
    esac
done

# Activate virtual environment if needed
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run 'python3 -m venv venv' first."
        exit 1
    fi
fi

echo "=========================================="
echo "Starting Printer Server"
echo "=========================================="
echo "Port: $PORT"
echo "Delay: $DELAY_MIN-$DELAY_MAX seconds"
echo "=========================================="
echo ""

PYTHONPATH="$PROJECT_ROOT" python3 printer/server.py \
    --port "$PORT" \
    --delay-min "$DELAY_MIN" \
    --delay-max "$DELAY_MAX"

