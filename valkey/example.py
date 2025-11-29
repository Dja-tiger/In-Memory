#!/usr/bin/env python3
"""
Valkey example - Redis-compatible with enhanced features
Valkey is a BSD-licensed fork of Redis, API-compatible
"""

import json
import time
import redis  # Valkey is Redis-compatible, uses same client

# Connect to Valkey (same as Redis)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def demo_compatibility():
    """Demonstrate Redis compatibility"""
    print("=== Valkey Redis Compatibility ===\n")

    # All Redis commands work the same
    r.set('compatibility', 'Valkey is 100% Redis compatible')
    print(f"SET compatibility -> {r.get('compatibility')}")

    # Data structures
    r.hset('user:1', mapping={'name': 'Valkey User', 'status': 'active'})
    print(f"HSET user:1 -> {r.hgetall('user:1')}")

    # Lists
    r.lpush('queue', 'task1', 'task2', 'task3')
    print(f"LPUSH queue -> Length: {r.llen('queue')}")

    # Sets
    r.sadd('tags', 'opensource', 'bsd', 'inmemory')
    print(f"SADD tags -> {r.smembers('tags')}")

def demo_performance_features():
    """Demonstrate performance optimizations"""
    print("\n=== Valkey Performance Features ===\n")

    # Multi-threading benefits (transparent to client)
    print("Valkey uses multi-threaded I/O for better performance")
    print("This is transparent - same API, better throughput")

    # Benchmark simulation
    print("\nSimulating high-throughput operations:")
    start = time.time()

    # Pipeline for batch operations
    pipe = r.pipeline()
    for i in range(10000):
        pipe.set(f'bench:key:{i}', f'value_{i}')

    results = pipe.execute()
    elapsed = time.time() - start

    print(f"Set 10,000 keys via pipeline in {elapsed:.3f} seconds")
    print(f"Throughput: {10000/elapsed:.0f} ops/sec")

    # Clean up
    for i in range(10000):
        r.delete(f'bench:key:{i}')

def demo_enhanced_commands():
    """Demonstrate any enhanced or new commands"""
    print("\n=== Valkey Enhanced Features ===\n")

    # Valkey maintains full Redis compatibility
    # Enhanced features are mostly internal optimizations

    # Improved memory management
    info = r.info('memory')
    print("Memory stats (optimized in Valkey):")
    for key in ['used_memory_human', 'used_memory_rss_human', 'mem_fragmentation_ratio']:
        if key in info:
            print(f"  {key}: {info[key]}")

    # Better cluster support
    print("\nCluster features:")
    print("  - Improved cluster stability")
    print("  - Better resharding performance")
    print("  - Enhanced failover mechanisms")

def demo_migration_from_redis():
    """Show migration path from Redis to Valkey"""
    print("\n=== Migration from Redis to Valkey ===\n")

    print("Migration is seamless:")
    print("1. Valkey uses the same RDB/AOF format")
    print("2. Same protocol (RESP)")
    print("3. Same client libraries")
    print("4. Same configuration format")

    # Demonstrate data persistence compatibility
    r.set('migration:test', 'Data persists across Redis/Valkey')
    r.bgsave()
    print("\nData saved in Redis-compatible format (RDB)")

    # Configuration compatibility
    config = r.config_get('maxmemory*')
    print("\nConfiguration (Redis-compatible):")
    for key, value in config.items():
        print(f"  {key}: {value}")

def demo_open_source_benefits():
    """Highlight open source benefits"""
    print("\n=== Open Source Benefits ===\n")

    print("Valkey advantages:")
    print("✓ BSD 3-Clause License (truly open source)")
    print("✓ Community-driven development")
    print("✓ No licensing restrictions")
    print("✓ Fork-friendly for custom needs")
    print("✓ Transparent governance model")

    # Version info
    info = r.info('server')
    if 'redis_version' in info:  # Valkey reports as Redis-compatible
        print(f"\nServer version: {info['redis_version']}")

def demo_monitoring():
    """Monitoring and metrics"""
    print("\n=== Monitoring Valkey ===\n")

    # Server stats
    info = r.info('stats')
    print("Server statistics:")
    for key in ['total_connections_received', 'total_commands_processed',
                'instantaneous_ops_per_sec', 'rejected_connections']:
        if key in info:
            print(f"  {key}: {info[key]}")

    # Replication info
    info = r.info('replication')
    print(f"\nReplication role: {info.get('role', 'unknown')}")

    # CPU usage
    info = r.info('cpu')
    if 'used_cpu_sys' in info:
        print(f"\nCPU usage:")
        print(f"  System: {info['used_cpu_sys']}")
        print(f"  User: {info['used_cpu_user']}")

def demo_advanced_patterns():
    """Advanced usage patterns"""
    print("\n=== Advanced Patterns ===\n")

    # Distributed lock pattern
    lock_key = 'lock:resource'
    lock_value = 'unique_id_123'

    # Try to acquire lock
    acquired = r.set(lock_key, lock_value, nx=True, ex=10)
    print(f"Lock acquisition: {'Success' if acquired else 'Failed'}")

    if acquired:
        # Do work...
        print("Performing critical work...")

        # Release lock safely
        lua_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        released = r.eval(lua_script, 1, lock_key, lock_value)
        print(f"Lock release: {'Success' if released else 'Failed'}")

    # Rate limiting pattern
    rate_limit_key = 'rate:user:123'
    r.delete(rate_limit_key)  # Clean slate

    print("\nRate limiting (10 requests per minute):")
    for i in range(12):
        pipe = r.pipeline()
        pipe.incr(rate_limit_key)
        pipe.expire(rate_limit_key, 60)
        current_count = pipe.execute()[0]

        if current_count <= 10:
            print(f"  Request {i+1}: Allowed (count: {current_count})")
        else:
            print(f"  Request {i+1}: Rate limited!")

def demo_clustering():
    """Cluster-related features"""
    print("\n=== Clustering Features ===\n")

    print("Valkey cluster improvements over Redis:")
    print("• Better performance under high load")
    print("• Improved resharding algorithms")
    print("• Enhanced monitoring capabilities")
    print("• More stable failover process")
    print("• Optimized slot migration")

    # In a real cluster setup, you would use:
    # from redis.cluster import RedisCluster
    # rc = RedisCluster(host='localhost', port=7000)

    print("\nCluster commands (when in cluster mode):")
    print("  CLUSTER INFO - Get cluster state")
    print("  CLUSTER NODES - List all nodes")
    print("  CLUSTER SLOTS - Show slot assignments")
    print("  CLUSTER FAILOVER - Manual failover")

def benchmark_comparison():
    """Simple benchmark comparison"""
    print("\n=== Performance Benchmark ===\n")

    operations = [
        ("SET", lambda i: r.set(f'perf:key:{i}', f'value_{i}')),
        ("GET", lambda i: r.get(f'perf:key:{i}')),
        ("INCR", lambda i: r.incr(f'perf:counter:{i}')),
        ("LPUSH", lambda i: r.lpush(f'perf:list:{i%100}', f'item_{i}')),
        ("SADD", lambda i: r.sadd(f'perf:set:{i%100}', f'member_{i}'))
    ]

    results = {}
    iterations = 1000

    for op_name, op_func in operations:
        start = time.time()
        for i in range(iterations):
            op_func(i)
        elapsed = time.time() - start
        results[op_name] = iterations / elapsed

    print("Operations per second:")
    for op_name, ops_per_sec in results.items():
        print(f"  {op_name:8} {ops_per_sec:>10.0f} ops/sec")

    # Cleanup
    for i in range(iterations):
        r.delete(f'perf:key:{i}', f'perf:counter:{i}')
    for i in range(100):
        r.delete(f'perf:list:{i}', f'perf:set:{i}')

if __name__ == "__main__":
    try:
        # Test connection
        r.ping()
        print("Connected to Valkey successfully!")
        print("=" * 50)
        print()

        # Run demos
        demo_compatibility()
        demo_performance_features()
        demo_enhanced_commands()
        demo_migration_from_redis()
        demo_open_source_benefits()
        demo_monitoring()
        demo_advanced_patterns()
        demo_clustering()
        benchmark_comparison()

        print("\n" + "=" * 50)
        print("Demo Complete!")

    except redis.ConnectionError:
        print("Error: Cannot connect to Valkey")
        print("Make sure Valkey is running on localhost:6379")
        print("\nTo start Valkey:")
        print("  docker run -d -p 6379:6379 valkey/valkey")
    except Exception as e:
        print(f"Error: {e}")