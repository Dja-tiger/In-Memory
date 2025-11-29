#!/usr/bin/env python3
"""
Apache Ignite example - Distributed In-Memory Computing Platform
"""

from pyignite import Client
from pyignite.datatypes import String, IntObject
import time

def demo_key_value_api(client):
    """Key-Value API operations"""
    print("=== Apache Ignite Key-Value API ===\n")

    # Create cache for simple string values
    cache = client.get_or_create_cache('users_cache')

    # Put simple string data (Apache Ignite Python client has issues with complex types)
    cache.put('user:1:name', 'Alice')
    cache.put('user:1:age', 30)
    cache.put('user:1:city', 'NYC')
    cache.put('user:2:name', 'Bob')
    cache.put('user:2:age', 25)
    cache.put('user:2:city', 'LA')
    print("Stored users in cache")

    # Get data
    name = cache.get('user:1:name')
    age = cache.get('user:1:age')
    city = cache.get('user:1:city')
    print(f"User 1: name={name}, age={age}, city={city}")

    # Update
    cache.put('user:1:age', 31)
    print(f"Updated user 1 age to 31")

    # Get multiple values
    keys = ['user:1:name', 'user:1:age', 'user:2:name', 'user:2:age']
    result = cache.get_all(keys)
    print(f"Multiple values: {result}")

def demo_sql_api(client):
    """SQL API for distributed queries"""
    print("\n=== Apache Ignite SQL API ===\n")

    # Create SQL table
    try:
        client.sql("DROP TABLE IF EXISTS Person")
    except:
        pass  # Table might not exist

    client.sql("""
        CREATE TABLE IF NOT EXISTS Person (
            id INT PRIMARY KEY,
            name VARCHAR,
            age INT,
            city VARCHAR
        ) WITH "template=replicated"
    """)
    print("Created SQL table 'Person'")

    # Insert data
    client.sql("""
        INSERT INTO Person (id, name, age, city) VALUES
        (1, 'Alice', 30, 'NYC'),
        (2, 'Bob', 25, 'LA'),
        (3, 'Charlie', 35, 'Chicago')
    """)
    print("Inserted data via SQL")

    # Query data
    result = client.sql(
        "SELECT * FROM Person WHERE age > ? ORDER BY age",
        query_args=[25]
    )

    print("People older than 25:")
    for row in result:
        print(f"  {row}")

    # Aggregation
    result = client.sql(
        "SELECT city, AVG(age) as avg_age FROM Person GROUP BY city"
    )

    print("\nAverage age by city:")
    for row in result:
        print(f"  {row[0]}: {row[1]:.1f}")

def demo_compute_grid(client):
    """Distributed compute capabilities"""
    print("\n=== Compute Grid ===\n")

    print("Apache Ignite Compute Features:")
    print("• Distributed task execution")
    print("• MapReduce operations")
    print("• Fork-Join processing")
    print("• Collocated processing")

    # Example: Distributed word count
    cache = client.get_or_create_cache('documents')

    # Store documents
    docs = {
        1: "Apache Ignite is fast",
        2: "Ignite provides SQL",
        3: "Distributed computing with Ignite"
    }

    for key, doc in docs.items():
        cache.put(key, doc)

    print(f"\nStored {len(docs)} documents for processing")

def demo_transactions(client):
    """ACID transactions across partitions"""
    print("\n=== ACID Transactions ===\n")

    # Simple transaction demo without special cache configuration
    cache = client.get_or_create_cache('accounts_simple')

    # Initial balances
    cache.put('acc1', 1000)
    cache.put('acc2', 500)

    print("Initial balances:")
    print(f"  Account 1: ${cache.get('acc1')}")
    print(f"  Account 2: ${cache.get('acc2')}")

    # Simple transfer without transactions for demo
    # (Real transactions require specific Ignite server configuration)
    acc1_balance = cache.get('acc1')
    acc2_balance = cache.get('acc2')

    transfer_amount = 200

    cache.put('acc1', acc1_balance - transfer_amount)
    cache.put('acc2', acc2_balance + transfer_amount)

    print(f"\nAfter transfer of ${transfer_amount}:")
    print(f"  Account 1: ${cache.get('acc1')}")
    print(f"  Account 2: ${cache.get('acc2')}")

    print("\nNote: Full ACID transactions require Ignite server configuration")

def demo_data_grid(client):
    """In-Memory Data Grid features"""
    print("\n=== In-Memory Data Grid ===\n")

    # Simplified cache creation - complex configs require server-side XML
    partitioned = client.get_or_create_cache('partitioned_cache')
    replicated = client.get_or_create_cache('replicated_cache')

    print("Cache modes:")
    print("• PARTITIONED - Data distributed across nodes")
    print("• REPLICATED - Full copy on each node")
    print("• LOCAL - Node-local cache")

    # Performance test
    start = time.time()
    for i in range(1000):
        partitioned.put(f'key{i}', f'value{i}')

    elapsed = time.time() - start
    print(f"\n1000 puts in {elapsed:.3f}s")
    print(f"Throughput: {1000/elapsed:.0f} ops/sec")

def demo_continuous_queries(client):
    """Real-time data processing with continuous queries"""
    print("\n=== Continuous Queries ===\n")

    print("Continuous Query Features:")
    print("• Real-time notifications on data changes")
    print("• Initial query for existing data")
    print("• Remote filters to reduce network traffic")
    print("• Local listeners for event processing")

    cache = client.get_or_create_cache('realtime_data')

    # Simulate real-time data
    for i in range(5):
        cache.put(f'sensor{i}', {'value': i * 10, 'timestamp': time.time()})

    print(f"\nSimulated {cache.get_size()} sensor readings")

def demo_persistence(client):
    """Native persistence with write-ahead log"""
    print("\n=== Native Persistence ===\n")

    print("Ignite Persistence Features:")
    print("• Write-Ahead Log (WAL)")
    print("• Checkpointing")
    print("• Full and incremental snapshots")
    print("• Automatic crash recovery")

    # Simplified cache creation (persistence requires server-side config)
    persistent_cache = client.get_or_create_cache('persistent_data')

    persistent_cache.put('config:setting1', 'value1')
    persistent_cache.put('config:setting2', 'value2')

    print("\nData stored (persistence requires server-side configuration)")

if __name__ == "__main__":
    try:
        # Connect to Ignite
        client = Client()
        client.connect('localhost', 10800)

        print("Connected to Apache Ignite!\n")
        print("=" * 50 + "\n")

        # Run demos
        demo_key_value_api(client)
        demo_sql_api(client)
        demo_compute_grid(client)
        demo_transactions(client)
        demo_data_grid(client)
        demo_continuous_queries(client)
        demo_persistence(client)

        print("\n" + "=" * 50)
        print("Apache Ignite: Distributed In-Memory Computing")

        # Close connection
        client.close()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Apache Ignite is running:")
        print("docker run -d -p 10800:10800 -p 11211:11211 -p 47100:47100 -p 47500:47500 apacheignite/ignite")