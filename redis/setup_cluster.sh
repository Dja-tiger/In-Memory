#!/bin/bash

# Redis Cluster Setup Script

set -e

echo "======================================="
echo "      Redis Cluster Setup"
echo "======================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# Stop and remove existing containers
echo -e "${YELLOW}Cleaning up existing Redis cluster containers...${NC}"
for port in 7000 7001 7002 7003 7004 7005; do
    docker stop redis-node-$port 2>/dev/null || true
    docker rm redis-node-$port 2>/dev/null || true
done

# Remove existing network
docker network rm redis-cluster-net 2>/dev/null || true

# Create network
echo -e "${GREEN}Creating cluster network...${NC}"
docker network create redis-cluster-net

# Function to create Redis node
create_redis_node() {
    local port=$1
    local cluster_port=$((port + 10000))

    echo -e "${GREEN}Starting Redis node on port $port...${NC}"

    # Create config directory
    mkdir -p /tmp/redis-cluster/$port

    # Create minimal cluster config
    cat > /tmp/redis-cluster/$port/redis.conf <<EOF
port $port
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
protected-mode no
bind 0.0.0.0
EOF

    # Start container
    docker run -d \
        --name redis-node-$port \
        --net redis-cluster-net \
        -p $port:$port \
        -p $cluster_port:$cluster_port \
        -v /tmp/redis-cluster/$port:/data \
        redis:latest \
        redis-server /data/redis.conf
}

# Start 6 Redis nodes (3 masters + 3 slaves)
echo
echo -e "${GREEN}Starting 6 Redis nodes...${NC}"
for port in 7000 7001 7002 7003 7004 7005; do
    create_redis_node $port
done

# Wait for nodes to start
echo
echo -e "${YELLOW}Waiting for nodes to start...${NC}"
sleep 5

# Get container IPs
echo
echo -e "${GREEN}Getting node IPs...${NC}"
declare -a node_ips

for port in 7000 7001 7002 7003 7004 7005; do
    ip=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis-node-$port)
    node_ips+=("$ip:$port")
    echo "  Node $port: $ip"
done

# Create the cluster
echo
echo -e "${GREEN}Creating Redis cluster...${NC}"
echo -e "${YELLOW}This will create 3 masters with 1 replica each${NC}"

# Build cluster create command
CLUSTER_HOSTS=""
for ip in "${node_ips[@]}"; do
    CLUSTER_HOSTS="$CLUSTER_HOSTS $ip"
done

# Execute cluster creation
docker run --rm -it --net redis-cluster-net redis:latest \
    redis-cli --cluster create $CLUSTER_HOSTS \
    --cluster-replicas 1 \
    --cluster-yes

echo
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}    Redis Cluster Setup Complete!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo

# Test the cluster
echo -e "${YELLOW}Testing cluster...${NC}"
docker run --rm --net redis-cluster-net redis:latest \
    redis-cli -c -h redis-node-7000 -p 7000 cluster info | head -5

echo
echo -e "${GREEN}Cluster is ready!${NC}"
echo
echo "Cluster nodes:"
echo "  Masters: localhost:7000, localhost:7001, localhost:7002"
echo "  Slaves:  localhost:7003, localhost:7004, localhost:7005"
echo
echo "Connect with:"
echo "  redis-cli -c -p 7000"
echo
echo "Test with Python:"
echo "  python3 example_cluster.py"
echo
echo "View cluster status:"
echo "  docker exec redis-node-7000 redis-cli cluster nodes"
echo
echo "Stop cluster:"
echo "  ./stop_cluster.sh"
echo