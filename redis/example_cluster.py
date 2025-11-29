#!/usr/bin/env python3
"""
Redis Cluster example - distributed Redis setup
"""

import time
import redis
from redis.cluster import RedisCluster
from redis.cluster import ClusterNode
import json

def demo_cluster_connection():
    """Connect to Redis Cluster"""
    print("=== Redis Cluster Connection ===\n")

    # Define cluster nodes
    startup_nodes = [
        ClusterNode("localhost", 7000),
        ClusterNode("localhost", 7001),
        ClusterNode("localhost", 7002)
    ]

    try:
        # Connect to cluster
        rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

        # Test connection
        rc.ping()
        print("Connected to Redis Cluster!")

        # Get cluster info
        cluster_info = rc.cluster_info()
        print(f"\nCluster state: {cluster_info.get('cluster_state', 'unknown')}")

        return rc
    except Exception as e:
        print(f"Could not connect to cluster: {e}")
        print("\nMake sure Redis Cluster is running on ports 7000-7005")
        return None

def demo_sharding(rc):
    """Demonstrate automatic sharding"""
    print("\n=== Automatic Sharding ===\n")

    # Keys will be automatically distributed across slots
    keys_to_set = 100
    print(f"Setting {keys_to_set} keys across the cluster...")

    for i in range(keys_to_set):
        rc.set(f"key:{i}", f"value_{i}")

    print(f"Set {keys_to_set} keys")

    # Check distribution
    nodes = rc.cluster_nodes()
    print("\nKey distribution across nodes:")

    for node in nodes:
        if node['flags'] == 'master':
            slots = node['slots']
            if slots:
                slot_range = f"{slots[0][0]}-{slots[0][1]}" if slots else "none"
                print(f"  Node {node['host']}:{node['port']}: slots {slot_range}")

def demo_hash_tags(rc):
    """Demonstrate hash tags for key grouping"""
    print("\n=== Hash Tags (Key Grouping) ===\n")

    # Keys with same hash tag go to same slot
    print("Keys with {user:123} hash tag go to same slot:")

    rc.set("{user:123}:profile", json.dumps({"name": "Alice", "age": 30}))
    rc.set("{user:123}:settings", json.dumps({"theme": "dark", "lang": "en"}))
    rc.set("{user:123}:session", "session_token_abc")

    # These can be fetched together efficiently
    keys = ["{user:123}:profile", "{user:123}:settings", "{user:123}:session"]
    values = rc.mget(keys)

    print("Retrieved related keys in single slot:")
    for key, value in zip(keys, values):
        print(f"  {key}: {value[:50]}...")

def demo_cluster_failover(rc):
    """Demonstrate cluster resilience"""
    print("\n=== Cluster Failover ===\n")

    print("Redis Cluster features:")
    print("• Automatic failover when master fails")
    print("• Data replication to slave nodes")
    print("• Continued operation during node failures")
    print("• Automatic resharding when adding/removing nodes")

    # Show cluster slots
    try:
        cluster_slots = rc.cluster_slots()
        print(f"\nCluster has {len(cluster_slots)} slot ranges")

        for slot_info in cluster_slots[:3]:  # Show first 3
            start, end = slot_info['slots'][0], slot_info['slots'][-1]
            master = slot_info['master']
            slaves = slot_info.get('slaves', [])

            print(f"\nSlots {start}-{end}:")
            print(f"  Master: {master['host']}:{master['port']}")
            if slaves:
                for slave in slaves:
                    print(f"  Slave: {slave['host']}:{slave['port']}")
    except:
        print("\nCluster slots command not available")

def demo_cluster_operations(rc):
    """Cluster-specific operations"""
    print("\n=== Cluster Operations ===\n")

    # Pipeline operations (limited in cluster mode)
    print("Pipeline operations (same slot only):")
    pipe = rc.pipeline()

    # These use hash tags to ensure same slot
    pipe.set("{batch}:1", "value1")
    pipe.set("{batch}:2", "value2")
    pipe.set("{batch}:3", "value3")
    results = pipe.execute()
    print(f"Pipeline results: {results}")

    # Transactions (limited to same slot)
    print("\nTransaction (same slot only):")
    pipe = rc.pipeline(transaction=True)
    pipe.set("{trans}:balance", 100)
    pipe.incrby("{trans}:balance", 50)
    pipe.decrby("{trans}:balance", 30)
    results = pipe.execute()

    final_balance = rc.get("{trans}:balance")
    print(f"Final balance after transaction: {final_balance}")

def demo_cluster_performance(rc):
    """Performance testing on cluster"""
    print("\n=== Cluster Performance ===\n")

    # Parallel writes across cluster
    start = time.time()

    for i in range(10000):
        # Keys distributed across all nodes
        rc.set(f"perf:key:{i}", f"value_{i}")

    elapsed = time.time() - start
    print(f"10,000 distributed writes in {elapsed:.3f} seconds")
    print(f"Throughput: {10000/elapsed:.0f} ops/sec")

    # Parallel reads
    start = time.time()

    for i in range(10000):
        rc.get(f"perf:key:{i}")

    elapsed = time.time() - start
    print(f"10,000 distributed reads in {elapsed:.3f} seconds")
    print(f"Throughput: {10000/elapsed:.0f} ops/sec")

    # Cleanup
    for i in range(10000):
        rc.delete(f"perf:key:{i}")

def demo_cluster_monitoring(rc):
    """Monitor cluster health"""
    print("\n=== Cluster Monitoring ===\n")

    # Cluster state
    try:
        info = rc.cluster_info()
        print("Cluster Info:")
        for key in ['cluster_state', 'cluster_slots_assigned',
                   'cluster_slots_ok', 'cluster_known_nodes']:
            if key in info:
                print(f"  {key}: {info[key]}")
    except:
        print("Could not get cluster info")

    # Node info
    print("\nNodes in cluster:")
    nodes = rc.cluster_nodes()

    masters = 0
    slaves = 0

    for node in nodes:
        if node['flags'] == 'master':
            masters += 1
            print(f"  Master: {node['host']}:{node['port']} (ID: {node['node_id'][:8]}...)")
        elif node['flags'] == 'slave':
            slaves += 1
            print(f"  Slave: {node['host']}:{node['port']} -> {node.get('master_id', 'unknown')[:8]}...")

    print(f"\nTotal: {masters} masters, {slaves} slaves")

def demo_cluster_resharding():
    """Explain cluster resharding"""
    print("\n=== Cluster Resharding ===\n")

    print("Adding nodes to cluster:")
    print("1. Start new Redis instance")
    print("2. Add to cluster: redis-cli --cluster add-node NEW_NODE EXISTING_NODE")
    print("3. Reshard: redis-cli --cluster reshard EXISTING_NODE")
    print("4. Rebalance: redis-cli --cluster rebalance EXISTING_NODE")

    print("\nRemoving nodes:")
    print("1. Reshard away from node: redis-cli --cluster reshard")
    print("2. Remove node: redis-cli --cluster del-node")

# Standalone demos that work without cluster
def demo_standalone_features():
    """Features that work in standalone Redis"""
    print("\n=== Standalone Redis Features ===\n")

    # Connect to standalone Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    try:
        r.ping()
        print("Connected to standalone Redis")

        # Demonstrate features
        print("\nFeatures available in standalone mode:")

        # 1. Full transactions
        pipe = r.pipeline(transaction=True)
        pipe.set("account:1", 100)
        pipe.set("account:2", 50)
        pipe.incrby("account:1", -30)
        pipe.incrby("account:2", 30)
        results = pipe.execute()
        print("✓ Full transactions across any keys")

        # 2. Pub/Sub
        print("✓ Pub/Sub messaging")

        # 3. Lua scripting
        lua_script = """
        return redis.call('get', KEYS[1])
        """
        print("✓ Lua scripting")

        # 4. All data structures
        r.lpush("list", "item1", "item2")
        r.sadd("set", "member1", "member2")
        r.zadd("zset", {"player1": 100, "player2": 200})
        r.hset("hash", mapping={"field1": "value1"})
        print("✓ All data structures")

        return r

    except redis.ConnectionError:
        print("Could not connect to standalone Redis on port 6379")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Redis Cluster Example")
    print("=" * 60)

    # Try cluster first
    print("\n1. Testing Redis Cluster (ports 7000-7005)...")
    rc = demo_cluster_connection()

    if rc:
        demo_sharding(rc)
        demo_hash_tags(rc)
        demo_cluster_failover(rc)
        demo_cluster_operations(rc)
        demo_cluster_performance(rc)
        demo_cluster_monitoring(rc)
        demo_cluster_resharding()
    else:
        print("\nCluster not available. Run ./setup_cluster.sh to create one.")

    # Test standalone
    print("\n" + "=" * 60)
    print("2. Testing Standalone Redis (port 6379)...")
    r = demo_standalone_features()

    if not rc and not r:
        print("\n" + "=" * 60)
        print("Neither cluster nor standalone Redis is available.")
        print("\nTo start standalone Redis:")
        print("  docker run -d -p 6379:6379 redis:latest")
        print("\nTo start Redis cluster:")
        print("  ./setup_cluster.sh")

    print("\n" + "=" * 60)
    print("Demo Complete")