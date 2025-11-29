#!/usr/bin/env python3
"""
Memcached example - simple key-value caching
"""

import json
import time
from pymemcache.client.base import Client
from pymemcache import serde

def json_serializer(key, value):
    if isinstance(value, str):
        return value.encode('utf-8'), 1
    return json.dumps(value).encode('utf-8'), 2

def json_deserializer(key, value, flags):
    if flags == 1:
        return value.decode('utf-8')
    elif flags == 2:
        return json.loads(value.decode('utf-8'))
    return value

# Connect to Memcached
client = Client(
    ('localhost', 11212),
    serializer=json_serializer,
    deserializer=json_deserializer
)

def demo_basic_operations():
    print("=== Basic Memcached Operations ===\n")

    # SET operation
    client.set('user:1', {'name': 'Alice', 'age': 30})
    print("SET user:1 -> {'name': 'Alice', 'age': 30}")

    # GET operation
    user = client.get('user:1')
    print(f"GET user:1 -> {user}")

    # ADD operation (only if key doesn't exist)
    result = client.add('user:2', {'name': 'Bob', 'age': 25})
    print(f"ADD user:2 -> Success: {result}")

    # REPLACE operation (only if key exists)
    result = client.replace('user:1', {'name': 'Alice', 'age': 31})
    print(f"REPLACE user:1 -> Success: {result}")

    # DELETE operation
    client.delete('user:2')
    print("DELETE user:2")

    # Check if deleted
    deleted_user = client.get('user:2')
    print(f"GET user:2 after delete -> {deleted_user}")

def demo_expiration():
    print("\n=== Expiration Example ===\n")

    # Set with TTL (3 seconds)
    client.set('session:123', {'user_id': 1, 'data': 'temp'}, expire=3)
    print("SET session:123 with 3 second TTL")

    # Get immediately
    session = client.get('session:123')
    print(f"GET session:123 immediately -> {session}")

    # Wait and try again
    print("Waiting 4 seconds...")
    time.sleep(4)
    expired_session = client.get('session:123')
    print(f"GET session:123 after expiry -> {expired_session}")

def demo_increment_decrement():
    print("\n=== Increment/Decrement Operations ===\n")

    # Set initial counter
    client.set('counter', '100')
    print("SET counter -> 100")

    # Increment
    new_value = client.incr('counter', 5)
    print(f"INCR counter by 5 -> {new_value}")

    # Decrement
    new_value = client.decr('counter', 3)
    print(f"DECR counter by 3 -> {new_value}")

def demo_cache_pattern():
    print("\n=== Cache-Aside Pattern Example ===\n")

    def get_user_from_db(user_id):
        # Simulate database query
        print(f"  [DB] Fetching user {user_id} from database...")
        time.sleep(0.5)  # Simulate DB latency
        return {'id': user_id, 'name': f'User_{user_id}', 'email': f'user{user_id}@example.com'}

    def get_user(user_id):
        cache_key = f'user:{user_id}'

        # Try cache first
        cached = client.get(cache_key)
        if cached:
            print(f"  [CACHE HIT] Found user {user_id} in cache")
            return cached

        # Cache miss - fetch from DB
        print(f"  [CACHE MISS] User {user_id} not in cache")
        user = get_user_from_db(user_id)

        # Store in cache for 60 seconds
        client.set(cache_key, user, expire=60)
        print(f"  [CACHE SET] Stored user {user_id} in cache")

        return user

    # First call - cache miss
    print("First call:")
    start = time.time()
    user = get_user(10)
    print(f"  Result: {user}")
    print(f"  Time: {(time.time() - start)*1000:.2f}ms\n")

    # Second call - cache hit
    print("Second call:")
    start = time.time()
    user = get_user(10)
    print(f"  Result: {user}")
    print(f"  Time: {(time.time() - start)*1000:.2f}ms")

def demo_multi_get():
    print("\n=== Multi-Get Operations ===\n")

    # Set multiple keys
    for i in range(1, 6):
        client.set(f'item:{i}', {'id': i, 'value': f'value_{i}'})
    print("SET item:1 through item:5")

    # Get multiple keys at once
    keys = [f'item:{i}' for i in range(1, 6)]
    items = client.get_many(keys)
    print(f"GET_MANY {keys}")
    for key, value in items.items():
        # Key might be bytes or string depending on pymemcache version
        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
        print(f"  {key_str} -> {value}")

def demo_stats():
    print("\n=== Memcached Statistics ===\n")

    try:
        stats = client.stats()

        # Display some interesting stats
        interesting_stats = [
            'curr_connections',
            'total_connections',
            'cmd_get',
            'cmd_set',
            'get_hits',
            'get_misses',
            'bytes',
            'curr_items'
        ]

        for stat_name in interesting_stats:
            # Handle both bytes and string keys
            stat_key = stat_name.encode() if isinstance(stat_name, str) else stat_name
            if stat_key in stats:
                value = stats[stat_key]
                # Decode if bytes
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                print(f"{stat_name}: {value}")
    except Exception as e:
        print(f"Could not retrieve stats: {e}")

if __name__ == "__main__":
    try:
        # Test connection
        client.set('test', 'ok')
        client.get('test')

        # Run demos
        demo_basic_operations()
        demo_expiration()
        demo_increment_decrement()
        demo_cache_pattern()
        demo_multi_get()
        demo_stats()

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Memcached is running on localhost:11211")
    finally:
        client.close()