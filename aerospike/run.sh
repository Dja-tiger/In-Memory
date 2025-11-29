#!/bin/bash

set -e

echo "==================================="
echo "    Aerospike Example Runner"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Stop existing container
docker stop aerospike-demo 2>/dev/null || true
docker rm aerospike-demo 2>/dev/null || true

# Start Aerospike
echo "Starting Aerospike..."
docker run -d \
    --name aerospike-demo \
    -p 3000:3000 \
    -p 3001:3001 \
    -p 3002:3002 \
    -p 3003:3003 \
    aerospike/aerospike-server

# Wait for ready
echo "Waiting for Aerospike to start..."
sleep 10

# Install dependencies
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q aerospike

# Run example
echo
python3 example.py

# AQL Shell
echo
echo "==================================="
echo "       Aerospike AQL Shell"
echo "==================================="
echo "Try: SELECT * FROM test.users"
echo "Type: exit to quit"
echo

docker exec -it aerospike-demo aql

# Cleanup
echo
read -p "Keep Aerospike running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    docker stop aerospike-demo
    docker rm aerospike-demo
fi

deactivate