#!/bin/bash

# Stop and remove Redis cluster

echo "======================================="
echo "    Stopping Redis Cluster"
echo "======================================="
echo

# Stop and remove containers
for port in 7000 7001 7002 7003 7004 7005; do
    echo "Stopping redis-node-$port..."
    docker stop redis-node-$port 2>/dev/null || true
    docker rm redis-node-$port 2>/dev/null || true
done

# Remove network
echo "Removing cluster network..."
docker network rm redis-cluster-net 2>/dev/null || true

# Cleanup temp files
echo "Cleaning up temporary files..."
rm -rf /tmp/redis-cluster/

echo
echo "Redis cluster stopped and cleaned up."