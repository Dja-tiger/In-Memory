#!/bin/bash

set -e

echo "==================================="
echo "    Tarantool Example Runner"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Stop existing container
docker stop tarantool-demo 2>/dev/null || true
docker rm tarantool-demo 2>/dev/null || true

# Start Tarantool
echo "Starting Tarantool..."
docker run -d \
    --name tarantool-demo \
    -p 3301:3301 \
    -e TARANTOOL_USER_NAME=admin \
    -e TARANTOOL_USER_PASSWORD=pass \
    tarantool/tarantool

# Wait for ready
echo "Waiting for Tarantool to start..."
sleep 5

# Install dependencies
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q tarantool

# Run example
echo
python3 example.py

# Interactive console
echo
echo "==================================="
echo "    Tarantool Console"
echo "==================================="
echo "Connecting to Tarantool console..."
echo "Try: box.space._space:select()"
echo "Type: \\q to exit"
echo

docker exec -it tarantool-demo tarantool -i

# Cleanup
echo
read -p "Keep Tarantool running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    docker stop tarantool-demo
    docker rm tarantool-demo
fi

deactivate