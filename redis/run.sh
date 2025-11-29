#!/bin/bash

# Redis example runner script

set -e

echo "==================================="
echo "       Redis Example Runner"
echo "==================================="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# Function to wait for Redis to be ready
wait_for_redis() {
    echo "Waiting for Redis to be ready..."
    for i in {1..30}; do
        if docker exec redis-demo redis-cli ping 2>/dev/null | grep -q PONG; then
            echo "Redis is ready!"
            return 0
        fi
        sleep 1
    done
    echo "Timeout waiting for Redis"
    return 1
}

# Stop and remove existing container if it exists
if docker ps -a | grep -q redis-demo; then
    echo "Stopping existing Redis container..."
    docker stop redis-demo 2>/dev/null || true
    docker rm redis-demo 2>/dev/null || true
fi

# Start Redis in Docker with persistence enabled
echo "Starting Redis in Docker..."
docker run -d \
    --name redis-demo \
    -p 6379:6379 \
    redis:latest \
    redis-server \
    --appendonly yes \
    --appendfsync everysec

# Wait for Redis to be ready
wait_for_redis

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
echo "      Running Redis Example"
echo "==================================="
echo

# Run the example
python3 example.py

echo
echo "==================================="
echo "         Redis CLI Demo"
echo "==================================="
echo
echo "Launching Redis CLI for interactive exploration..."
echo "Type 'exit' to quit"
echo

# Launch Redis CLI
docker exec -it redis-demo redis-cli

echo
echo "==================================="
echo "           Cleanup"
echo "==================================="
echo

# Ask user if they want to keep the container running
read -p "Keep Redis container running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Redis container..."
    docker stop redis-demo
    docker rm redis-demo
    echo "Redis container removed."
else
    echo "Redis container is still running."
    echo "To connect: docker exec -it redis-demo redis-cli"
    echo "To stop: docker stop redis-demo && docker rm redis-demo"
fi

deactivate