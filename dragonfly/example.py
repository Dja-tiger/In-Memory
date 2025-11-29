#!/usr/bin/env python3
"""
Dragonfly example - Ultra-fast Redis-compatible in-memory store
Dragonfly is 25x faster than Redis on multi-core machines
"""

import json
import time
import redis  # Dragonfly is Redis-compatible
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Connect to Dragonfly
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def demo_basic_operations():
    """Basic operations - Redis compatible"""
    print("=== Dragonfly Basic Operations ===")
    print("Dragonfly is 100% Redis API compatible\n")

    # All Redis operations work
    r.set('dragonfly', 'ultra-fast')
    print(f"SET dragonfly -> {r.get('dragonfly')}")

    # JSON support (native)
    user = {'name': 'Dragon', 'speed': 'ultra-fast', 'cores': 'all'}
    r.set('user:1', json.dumps(user))
    print(f"JSON storage -> {json.loads(r.get('user:1'))}")

def demo_performance():
    """Demonstrate Dragonfly's performance"""
    print("\n=== Dragonfly Performance Demo ===")
    print("Dragonfly uses all CPU cores efficiently\n")

    def parallel_writes(thread_id, count=1000):
        for i in range(count):
            r.set(f'perf:thread{thread_id}:key{i}', f'value_{i}')
        return thread_id

    # Parallel writes (Dragonfly handles this efficiently)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(parallel_writes, i) for i in range(4)]
        for future in as_completed(futures):
            print(f"Thread {future.result()} completed")
    
    elapsed = time.time() - start
    print(f"\n4000 parallel writes in {elapsed:.2f} seconds")
    print(f"Throughput: {4000/elapsed:.0f} ops/sec")

    # Cleanup
    for i in range(4):
        for j in range(1000):
            r.delete(f'perf:thread{i}:key{j}')

def demo_memory_efficiency():
    """Show memory efficiency features"""
    print("\n=== Memory Efficiency ===")
    print("Dragonfly uses ~30% less memory than Redis\n")

    info = r.info('memory')
    print("Memory stats:")
    for key in ['used_memory_human', 'used_memory_rss_human']:
        if key in info:
            print(f"  {key}: {info[key]}")

    print("\nDragonfly features:")
    print("• Dashtable instead of dict")
    print("• Better memory allocator")
    print("• Compressed data structures")
    print("• Efficient expiration handling")

def demo_advanced_features():
    """Dragonfly-specific optimizations"""
    print("\n=== Dragonfly Advanced Features ===")

    print("\n1. Vertical scaling:")
    print("   Dragonfly scales to 100+ CPU cores")
    print("   Redis is limited to single-threaded")

    print("\n2. Snapshot consistency:")
    print("   Point-in-time snapshots without blocking")
    try:
        r.bgsave()
        print("   BGSAVE initiated (non-blocking)")
    except Exception as e:
        # Dragonfly uses SAVE instead of BGSAVE
        try:
            r.save()
            print("   SAVE completed")
        except:
            print("   Snapshots supported but command may differ")

    print("\n3. Better caching:")
    print("   Improved eviction algorithms")
    print("   Predictive cache warming")

if __name__ == "__main__":
    try:
        r.ping()
        print("Connected to Dragonfly!\n")
        print("=" * 50)

        demo_basic_operations()
        demo_performance()
        demo_memory_efficiency()
        demo_advanced_features()

        print("\n" + "=" * 50)
        print("Dragonfly: 25× Redis performance!")

    except redis.ConnectionError:
        print("Error: Cannot connect to Dragonfly")
        print("Start Dragonfly: docker run -p 6379:6379 docker.dragonflydb.io/dragonflydb/dragonfly")