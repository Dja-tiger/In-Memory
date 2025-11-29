#!/bin/bash

set -e

echo "==================================="
echo "   Apache Ignite Example Runner"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Stop existing container
docker stop ignite-demo 2>/dev/null || true
docker rm ignite-demo 2>/dev/null || true

# Start Apache Ignite
echo "Starting Apache Ignite..."
docker run -d \
    --name ignite-demo \
    -p 10800:10800 \
    -p 11211:11211 \
    -p 47100:47100 \
    -p 47500:47500 \
    -p 49112:49112 \
    apacheignite/ignite

# Wait for ready
echo "Waiting for Ignite to start (this may take a minute)..."
sleep 15

# Install dependencies
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q pyignite

# Run example
echo
python3 example.py

# SQL Shell
echo
echo "==================================="
echo "    Apache Ignite SQL Shell"
echo "==================================="
echo "Connecting to SQL shell..."
echo "Try: SELECT * FROM Person;"
echo "Type: !quit to exit"
echo

docker exec -it ignite-demo /opt/ignite/apache-ignite/bin/sqlline.sh \
    --verbose=false \
    -u "jdbc:ignite:thin://127.0.0.1/"

# Cleanup
echo
read -p "Keep Apache Ignite running? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    docker stop ignite-demo
    docker rm ignite-demo
fi

deactivate