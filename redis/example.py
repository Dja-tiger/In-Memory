#!/usr/bin/env python3
"""
Redis example - various data structures and patterns
"""

import json
import time
import redis
from datetime import datetime, timedelta

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def demo_basic_operations():
    print("=== Basic Redis Operations ===\n")

    # String operations
    r.set('name', 'Redis')
    print("SET name 'Redis'")

    name = r.get('name')
    print(f"GET name -> {name}")

    # Set with expiration
    r.setex('token', 10, 'abc123')
    print("SETEX token 10 'abc123' (expires in 10 seconds)")

    # Set if not exists
    result = r.setnx('name', 'NewValue')
    print(f"SETNX name 'NewValue' -> {result} (false because key exists)")

    # Multiple operations
    r.mset({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'})
    print("MSET key1 value1 key2 value2 key3 value3")

    values = r.mget(['key1', 'key2', 'key3'])
    print(f"MGET key1 key2 key3 -> {values}")

def demo_list_operations():
    print("\n=== List Operations ===\n")

    # Clear list first
    r.delete('queue')

    # Push to list
    r.lpush('queue', 'task1', 'task2', 'task3')
    print("LPUSH queue task1 task2 task3")

    r.rpush('queue', 'task4')
    print("RPUSH queue task4")

    # Get list length
    length = r.llen('queue')
    print(f"LLEN queue -> {length}")

    # Get range
    items = r.lrange('queue', 0, -1)
    print(f"LRANGE queue 0 -1 -> {items}")

    # Pop from list
    item = r.lpop('queue')
    print(f"LPOP queue -> {item}")

    item = r.rpop('queue')
    print(f"RPOP queue -> {item}")

    # Blocking pop (timeout after 1 second)
    print("BLPOP queue 1 (blocking pop with 1s timeout)...")
    item = r.blpop('queue', timeout=1)
    print(f"Result -> {item}")

def demo_set_operations():
    print("\n=== Set Operations ===\n")

    # Clear sets first
    r.delete('users:online', 'users:premium', 'users:active')

    # Add to sets
    r.sadd('users:online', 'user1', 'user2', 'user3')
    print("SADD users:online user1 user2 user3")

    r.sadd('users:premium', 'user2', 'user3', 'user4')
    print("SADD users:premium user2 user3 user4")

    # Check membership
    is_member = r.sismember('users:online', 'user1')
    print(f"SISMEMBER users:online user1 -> {is_member}")

    # Get all members
    members = r.smembers('users:online')
    print(f"SMEMBERS users:online -> {members}")

    # Set operations
    intersection = r.sinter('users:online', 'users:premium')
    print(f"SINTER users:online users:premium -> {intersection}")

    union = r.sunion('users:online', 'users:premium')
    print(f"SUNION users:online users:premium -> {union}")

    diff = r.sdiff('users:online', 'users:premium')
    print(f"SDIFF users:online users:premium -> {diff}")

def demo_sorted_set_operations():
    print("\n=== Sorted Set (ZSet) Operations ===\n")

    # Clear sorted set first
    r.delete('leaderboard')

    # Add scores
    r.zadd('leaderboard', {'player1': 100, 'player2': 200, 'player3': 150})
    print("ZADD leaderboard 100 player1 200 player2 150 player3")

    # Increment score
    new_score = r.zincrby('leaderboard', 50, 'player1')
    print(f"ZINCRBY leaderboard 50 player1 -> {new_score}")

    # Get rank (0-indexed)
    rank = r.zrank('leaderboard', 'player1')
    print(f"ZRANK leaderboard player1 -> {rank}")

    # Get reverse rank (top players)
    rank = r.zrevrank('leaderboard', 'player2')
    print(f"ZREVRANK leaderboard player2 -> {rank}")

    # Get top 3 players with scores
    top_players = r.zrevrange('leaderboard', 0, 2, withscores=True)
    print("ZREVRANGE leaderboard 0 2 WITHSCORES:")
    for player, score in top_players:
        print(f"  {player}: {score}")

def demo_hash_operations():
    print("\n=== Hash Operations ===\n")

    # Clear hash first
    r.delete('user:1')

    # Set hash fields
    r.hset('user:1', mapping={'name': 'Alice', 'age': '30', 'city': 'NYC'})
    print("HSET user:1 name Alice age 30 city NYC")

    # Get single field
    name = r.hget('user:1', 'name')
    print(f"HGET user:1 name -> {name}")

    # Get all fields
    user = r.hgetall('user:1')
    print(f"HGETALL user:1 -> {user}")

    # Increment field
    new_age = r.hincrby('user:1', 'age', 1)
    print(f"HINCRBY user:1 age 1 -> {new_age}")

    # Check field exists
    exists = r.hexists('user:1', 'email')
    print(f"HEXISTS user:1 email -> {exists}")

    # Get all field names
    fields = r.hkeys('user:1')
    print(f"HKEYS user:1 -> {fields}")

def demo_pub_sub():
    print("\n=== Pub/Sub Pattern ===\n")

    import threading

    def subscriber():
        pubsub = r.pubsub()
        pubsub.subscribe('notifications')

        for message in pubsub.listen():
            if message['type'] == 'message':
                print(f"  [SUBSCRIBER] Received: {message['data']}")
                if message['data'] == 'STOP':
                    break

        pubsub.unsubscribe('notifications')
        pubsub.close()

    # Start subscriber in background thread
    sub_thread = threading.Thread(target=subscriber)
    sub_thread.start()

    time.sleep(0.5)  # Give subscriber time to connect

    # Publish messages
    print("Publishing messages to 'notifications' channel:")
    r.publish('notifications', 'Hello World!')
    time.sleep(0.1)
    r.publish('notifications', 'Message 2')
    time.sleep(0.1)
    r.publish('notifications', 'STOP')

    sub_thread.join()

def demo_transactions():
    print("\n=== Transactions (MULTI/EXEC) ===\n")

    # Clear keys first
    r.delete('account:1', 'account:2')
    r.set('account:1', '100')
    r.set('account:2', '50')

    print("Initial state:")
    print(f"  account:1 = {r.get('account:1')}")
    print(f"  account:2 = {r.get('account:2')}")

    # Start transaction
    pipe = r.pipeline()

    # Queue commands
    pipe.decrby('account:1', 30)
    pipe.incrby('account:2', 30)

    # Execute atomically
    result = pipe.execute()
    print("\nAfter transaction (transfer 30 from account:1 to account:2):")
    print(f"  account:1 = {r.get('account:1')}")
    print(f"  account:2 = {r.get('account:2')}")

def demo_lua_scripting():
    print("\n=== Lua Scripting ===\n")

    # Define a Lua script for atomic compare and swap
    lua_script = """
    local current = redis.call('get', KEYS[1])
    if current == ARGV[1] then
        redis.call('set', KEYS[1], ARGV[2])
        return 1
    else
        return 0
    end
    """

    # Register script
    cas = r.register_script(lua_script)

    # Set initial value
    r.set('counter', '100')
    print("SET counter 100")

    # Try to update if value is 100
    result = cas(keys=['counter'], args=['100', '200'])
    print(f"CAS counter: if 100 then set 200 -> Success: {result}")
    print(f"  New value: {r.get('counter')}")

    # Try again (should fail)
    result = cas(keys=['counter'], args=['100', '300'])
    print(f"CAS counter: if 100 then set 300 -> Success: {result}")
    print(f"  Value unchanged: {r.get('counter')}")

def demo_persistence_info():
    print("\n=== Persistence Info ===\n")

    # Get persistence info
    info = r.info('persistence')

    print("Key persistence metrics:")
    for key in ['rdb_last_save_time', 'rdb_changes_since_last_save',
                'aof_enabled', 'aof_rewrite_in_progress']:
        if key in info:
            print(f"  {key}: {info[key]}")

    # Trigger manual save (background)
    r.bgsave()
    print("\nTriggered background save (BGSAVE)")

def demo_cache_patterns():
    print("\n=== Cache Patterns ===\n")

    # Cache-Aside Pattern
    def get_user(user_id):
        cache_key = f'cache:user:{user_id}'

        # Try cache
        cached = r.get(cache_key)
        if cached:
            print(f"  Cache HIT for user {user_id}")
            return json.loads(cached)

        # Simulate DB fetch
        print(f"  Cache MISS for user {user_id}, fetching from DB...")
        user = {'id': user_id, 'name': f'User_{user_id}', 'timestamp': str(datetime.now())}

        # Store in cache with TTL
        r.setex(cache_key, 60, json.dumps(user))
        return user

    print("Cache-Aside Pattern:")
    user = get_user(1)
    print(f"  Result: {user}")

    user = get_user(1)  # Should hit cache
    print(f"  Result: {user}")

    # Write-Through Pattern
    def update_user(user_id, data):
        cache_key = f'cache:user:{user_id}'

        # Update cache
        r.setex(cache_key, 60, json.dumps(data))

        # Simulate DB update
        print(f"  Updated user {user_id} in cache and DB")
        return data

    print("\nWrite-Through Pattern:")
    updated = update_user(1, {'id': 1, 'name': 'Updated_User_1'})
    print(f"  Result: {updated}")

def demo_monitoring():
    print("\n=== Monitoring & Stats ===\n")

    # Get general info
    info = r.info()

    print("Server info:")
    print(f"  Redis version: {info.get('redis_version', 'N/A')}")
    print(f"  Uptime (seconds): {info.get('uptime_in_seconds', 'N/A')}")
    print(f"  Connected clients: {info.get('connected_clients', 'N/A')}")
    print(f"  Used memory: {info.get('used_memory_human', 'N/A')}")
    print(f"  Total commands processed: {info.get('total_commands_processed', 'N/A')}")

    # Get slow queries
    slow_queries = r.slowlog_get(5)
    if slow_queries:
        print("\nRecent slow queries:")
        for query in slow_queries[:3]:
            print(f"  Command: {' '.join(query['command'])[:50]}...")
            print(f"  Duration: {query['duration']} microseconds")

if __name__ == "__main__":
    try:
        # Test connection
        r.ping()
        print("Connected to Redis successfully!\n")

        # Run demos
        demo_basic_operations()
        demo_list_operations()
        demo_set_operations()
        demo_sorted_set_operations()
        demo_hash_operations()
        demo_pub_sub()
        demo_transactions()
        demo_lua_scripting()
        demo_persistence_info()
        demo_cache_patterns()
        demo_monitoring()

        print("\n=== Demo Complete ===")

    except redis.ConnectionError:
        print("Error: Cannot connect to Redis")
        print("Make sure Redis is running on localhost:6379")
    except Exception as e:
        print(f"Error: {e}")