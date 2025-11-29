#!/bin/bash

# Memcached example runner script

set -e

echo "==================================="
echo "    Memcached Example Runner"
echo "==================================="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# Function to wait for Memcached to be ready
wait_for_memcached() {
    echo "Waiting for Memcached to be ready..."
    for i in {1..30}; do
        if nc -zv localhost 11211 2>/dev/null; then
            echo "Memcached is ready!"
            return 0
        fi
        sleep 1
    done
    echo "Timeout waiting for Memcached"
    return 1
}

# Stop and remove existing container if it exists
if docker ps -a | grep -q memcached-demo; then
    echo "Stopping existing Memcached container..."
    docker stop memcached-demo 2>/dev/null || true
    docker rm memcached-demo 2>/dev/null || true
fi

# Start Memcached in Docker
echo "Starting Memcached in Docker..."
docker run -d \
    --name memcached-demo \
    -p 11211:11211 \
    memcached:latest \
    memcached -m 64 -vv

# Wait for Memcached to be ready
wait_for_memcached

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
pip install -q pymemcache

echo
echo "==================================="
echo "    Running Memcached Example"
echo "==================================="
echo

# Run the example
python3 example.py

echo
echo "==================================="
echo "    Cleanup"
echo "==================================="
echo

# Ask user if they want to keep the container running
read -p "Keep Memcached container running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Memcached container..."
    docker stop memcached-demo
    docker rm memcached-demo
    echo "Memcached container removed."
else
    echo "Memcached container is still running."
    echo "To connect: telnet localhost 11211"
    echo "To stop: docker stop memcached-demo && docker rm memcached-demo"
fi

deactivate