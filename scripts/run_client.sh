#!/bin/bash

# Script to run a client for manual testing
# Usage: ./scripts/run_client.sh --id ID --port PORT --server SERVER [--clients CLIENTS] [--job-interval-min MIN] [--job-interval-max MAX]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

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
echo "Starting Client"
echo "=========================================="
echo ""

PYTHONPATH="$PROJECT_ROOT" python3 client/main.py "$@"

