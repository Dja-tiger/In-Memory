#!/bin/bash

# Valkey example runner script

set -e

echo "==================================="
echo "      Valkey Example Runner"
echo "==================================="
echo
echo "Valkey - Open Source Redis Alternative"
echo "100% Redis Protocol Compatible"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# Function to wait for Valkey to be ready
wait_for_valkey() {
    echo "Waiting for Valkey to be ready..."
    for i in {1..30}; do
        if docker exec valkey-demo redis-cli ping 2>/dev/null | grep -q PONG; then
            echo "Valkey is ready!"
            return 0
        fi
        sleep 1
    done
    echo "Timeout waiting for Valkey"
    return 1
}

# Stop and remove existing container if it exists
if docker ps -a | grep -q valkey-demo; then
    echo "Stopping existing Valkey container..."
    docker stop valkey-demo 2>/dev/null || true
    docker rm valkey-demo 2>/dev/null || true
fi

# Start Valkey in Docker
echo "Starting Valkey in Docker..."
docker run -d \
    --name valkey-demo \
    -p 6379:6379 \
    valkey/valkey:latest \
    valkey-server \
    --appendonly yes \
    --appendfsync everysec \
    --io-threads 4 \
    --io-threads-do-reads yes

# Wait for Valkey to be ready
wait_for_valkey

echo
echo "==================================="
echo "    Installing Python Dependencies"
echo "==================================="
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -q redis

echo
echo "==================================="
echo "      Running Valkey Example"
echo "==================================="
echo

# Run the example
python3 example.py

echo
echo "==================================="
echo "    Valkey vs Redis Comparison"
echo "==================================="
echo
echo "Key Differences:"
echo "• License: BSD 3-Clause (Valkey) vs SSPLv1/RSALv2 (Redis)"
echo "• Performance: ~37% faster on multi-core systems"
echo "• Community: Open governance model"
echo "• Compatibility: 100% Redis protocol compatible"
echo

echo "==================================="
echo "      Interactive CLI Session"
echo "==================================="
echo
echo "Launching Valkey CLI (Redis-compatible)..."
echo "Try these commands:"
echo "  INFO server"
echo "  CONFIG GET io-threads"
echo "  CLIENT LIST"
echo "Type 'exit' to quit"
echo

# Launch CLI
docker exec -it valkey-demo redis-cli

echo
echo "==================================="
echo "           Cleanup"
echo "==================================="
echo

# Ask user if they want to keep the container running
read -p "Keep Valkey container running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Valkey container..."
    docker stop valkey-demo
    docker rm valkey-demo
    echo "Valkey container removed."
else
    echo "Valkey container is still running."
    echo "To connect: docker exec -it valkey-demo redis-cli"
    echo "To stop: docker stop valkey-demo && docker rm valkey-demo"
fi

deactivate