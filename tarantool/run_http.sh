#!/bin/bash

set -e

echo "==================================="
echo "  Tarantool HTTP Server Example"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Stop existing containers
docker stop tarantool-http 2>/dev/null || true
docker rm tarantool-http 2>/dev/null || true

# Build custom image with HTTP server
echo "Building Tarantool image with HTTP server..."
docker build -t tarantool-http .

# Start Tarantool with HTTP server
echo "Starting Tarantool HTTP server..."
docker run -d \
    --name tarantool-http \
    -p 8080:8080 \
    -p 3301:3301 \
    tarantool-http

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if docker ps | grep -q tarantool-http; then
    echo "Server started successfully!"
    echo

    # Install dependencies
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q requests

    # Run HTTP example
    echo "Running HTTP API examples..."
    echo
    python3 http_example.py

    # Show API endpoints
    echo
    echo "==================================="
    echo "    Available API Endpoints"
    echo "==================================="
    echo
    echo "Health Check:"
    echo "  curl http://localhost:8080/health"
    echo
    echo "Users API:"
    echo "  curl http://localhost:8080/api/users"
    echo "  curl -X POST http://localhost:8080/api/users \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"name\":\"Test\",\"email\":\"test@example.com\",\"age\":25}'"
    echo
    echo "Stats:"
    echo "  curl http://localhost:8080/api/stats"
    echo
    echo "Tarantool Console:"
    echo "  docker exec -it tarantool-http tarantoolctl connect localhost:3301"
    echo

    deactivate

    # Ask to keep running
    echo
    read -p "Keep server running? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        docker stop tarantool-http
        docker rm tarantool-http
        echo "Server stopped and removed"
    else
        echo "Server is running at http://localhost:8080"
        echo "To stop: docker stop tarantool-http"
    fi
else
    echo "Error: Failed to start server"
    docker logs tarantool-http
    exit 1
fi