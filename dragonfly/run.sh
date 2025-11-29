#!/bin/bash

set -e

echo "==================================="
echo "     Dragonfly Example Runner"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Stop existing container
docker stop dragonfly-demo 2>/dev/null || true
docker rm dragonfly-demo 2>/dev/null || true

# Start Dragonfly
echo "Starting Dragonfly (25× faster than Redis)..."
docker run -d \
    --name dragonfly-demo \
    -p 6379:6379 \
    --ulimit memlock=-1 \
    docker.dragonflydb.io/dragonflydb/dragonfly

# Wait for ready
sleep 3

# Install dependencies
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q redis

# Run example
echo
python3 example.py

# Cleanup
echo
read -p "Keep Dragonfly running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    docker stop dragonfly-demo
    docker rm dragonfly-demo
fi

deactivate