#!/usr/bin/env python3
"""
Aerospike example - High-performance NoSQL database
"""

import aerospike
from aerospike import exception as ex
import time
import sys

# Configuration
config = {
    'hosts': [('localhost', 3000)]
}

def demo_basic_operations(client):
    """Basic CRUD operations"""
    print("=== Aerospike Basic Operations ===\n")

    # Key: (namespace, set, primary_key)
    key = ('test', 'users', 'user1')

    # Write record
    record = {
        'name': 'Alice',
        'age': 30,
        'city': 'San Francisco',
        'balance': 1000.50
    }
    client.put(key, record)
    print(f"PUT: {key} -> {record}")

    # Read record
    (key, metadata, record) = client.get(key)
    print(f"GET: {record}")

    # Update record
    client.put(key, {'age': 31})
    (key, metadata, record) = client.get(key)
    print(f"UPDATE age: {record}")

    # Delete record
    client.remove(key)
    print(f"REMOVED: {key}")

def demo_batch_operations(client):
    """Batch operations for performance"""
    print("\n=== Batch Operations ===\n")

    # Batch write
    keys = []
    records = []
    for i in range(10):
        key = ('test', 'batch', f'item{i}')
        keys.append(key)
        record = {'id': i, 'value': f'data_{i}'}
        records.append(record)
        client.put(key, record)

    print(f"Batch wrote {len(keys)} records")

    # Batch read
    records = []
    for key in keys:
        try:
            (key, metadata, record) = client.get(key)
            if record:
                records.append(record)
        except:
            pass
    print(f"Batch read {len(records)} records")

def demo_secondary_indexes(client):
    """Secondary index queries"""
    print("\n=== Secondary Indexes ===\n")

    # Create index
    try:
        client.index_integer_create('test', 'users', 'age', 'age_idx')
        print("Created index on 'age'")
    except ex.IndexFoundError:
        print("Index 'age_idx' already exists")

    # Insert test data
    for i in range(1, 6):
        key = ('test', 'users', f'user{i}')
        record = {
            'name': f'User{i}',
            'age': 20 + i * 5,
            'city': 'NYC' if i % 2 == 0 else 'LA'
        }
        client.put(key, record)

    # Query using index
    query = client.query('test', 'users')
    query.where(aerospike.predicates.between('age', 25, 35))

    records = []
    for record in query.results():
        records.append(record)

    print(f"Users with age 25-35: {len(records)} found")

def demo_udf_operations(client):
    """User Defined Functions (UDF) in Lua"""
    print("\n=== UDF Operations ===\n")

    # Register UDF
    lua_code = """
    function increment(rec, bin_name, value)
        if not aerospike:exists(rec) then
            rec[bin_name] = value
        else
            rec[bin_name] = rec[bin_name] + value
        end
        aerospike:update(rec)
        return rec[bin_name]
    end
    """

    # Note: In production, save as .lua file and register
    print("UDF example (Lua):")
    print("- Atomic increment operations")
    print("- Server-side data processing")
    print("- MapReduce aggregations")

def demo_hybrid_memory(client):
    """Demonstrate Hybrid Memory Architecture"""
    print("\n=== Hybrid Memory Architecture ===\n")

    print("Aerospike HMA Features:")
    print("• Indexes in RAM (64 bytes/record)")
    print("• Data on SSD (direct device access)")
    print("• Smart caching of hot data")
    print("• 10× cost reduction vs pure RAM")

    # Performance test
    start = time.time()
    for i in range(1000):
        key = ('test', 'perf', f'key{i}')
        record = {'data': f'x' * 1000}  # 1KB record
        client.put(key, record)

    elapsed = time.time() - start
    print(f"\n1000 writes (1KB each) in {elapsed:.3f}s")
    print(f"Throughput: {1000/elapsed:.0f} ops/sec")

def demo_complex_types(client):
    """Complex data types and operations"""
    print("\n=== Complex Data Types ===\n")

    key = ('test', 'complex', 'doc1')

    # Complex document
    document = {
        'user': {
            'id': 1,
            'name': 'Alice',
            'tags': ['premium', 'active'],
            'scores': [95, 87, 92]
        },
        'metadata': {
            'created': '2024-01-01',
            'version': 2
        }
    }

    client.put(key, document)
    print(f"Stored complex document: {key}")

    # List operations
    list_key = ('test', 'lists', 'list1')
    client.put(list_key, {'items': [1, 2, 3, 4, 5]})

    # List operations can be done directly
    (key, metadata, record) = client.get(list_key)
    items = record['items']
    items.append(6)
    client.put(list_key, {'items': items})

    (key, metadata, record) = client.get(list_key)
    print(f"List after append: {record['items']}")

if __name__ == "__main__":
    try:
        # Connect
        client = aerospike.client(config).connect()
        print("Connected to Aerospike!\n")
        print("=" * 50 + "\n")

        # Run demos
        demo_basic_operations(client)
        demo_batch_operations(client)
        demo_secondary_indexes(client)
        demo_udf_operations(client)
        demo_hybrid_memory(client)
        demo_complex_types(client)

        print("\n" + "=" * 50)
        print("Aerospike: Enterprise-Grade NoSQL")

        # Close connection
        client.close()

    except ex.AerospikeError as e:
        print(f"Error: {e}")
        print("\nMake sure Aerospike is running:")
        print("docker run -d -p 3000:3000 -p 3001:3001 -p 3002:3002 -p 3003:3003 aerospike/aerospike-server")
        sys.exit(1)