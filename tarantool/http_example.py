#!/usr/bin/env python3
"""
Tarantool HTTP Server example - REST API demonstration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def demo_health_check():
    """Check server health"""
    print("=== Health Check ===\n")

    response = requests.get(f"{BASE_URL}/health")
    health = response.json()
    print(f"Status: {health['status']}")
    print(f"Uptime: {health['uptime']:.2f} seconds")
    print(f"Memory: {health['memory'] / 1024 / 1024:.2f} MB")
    print(f"Version: {health['version']}")

def demo_user_crud():
    """User CRUD operations via REST API"""
    print("\n=== User CRUD Operations ===\n")

    # Create users
    users_data = [
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 25},
        {"name": "Charlie", "email": "charlie@example.com", "age": 35}
    ]

    created_users = []
    for user_data in users_data:
        response = requests.post(f"{BASE_URL}/api/users", json=user_data)
        if response.status_code == 201:
            user = response.json()
            created_users.append(user)
            print(f"Created user: {user['name']} (ID: {user['id']})")
        elif response.status_code == 409:
            print(f"User with email {user_data['email']} already exists")

    # Get all users
    response = requests.get(f"{BASE_URL}/api/users")
    all_users = response.json()
    print(f"\nTotal users: {len(all_users)}")

    # Get specific user
    if created_users:
        user_id = created_users[0]['id']
        response = requests.get(f"{BASE_URL}/api/users/{user_id}")
        user = response.json()
        print(f"\nFetched user {user_id}: {user['name']} ({user['email']})")

        # Update user
        response = requests.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"age": 31}
        )
        if response.status_code == 200:
            updated_user = response.json()
            print(f"Updated user {user_id} age to {updated_user['age']}")

    # Search users
    response = requests.get(f"{BASE_URL}/api/users/search", params={"email": "example.com"})
    search_results = response.json()
    print(f"\nUsers with 'example.com' in email: {len(search_results)}")

def demo_batch_operations():
    """Batch insert operations"""
    print("\n=== Batch Operations ===\n")

    batch_users = {
        "users": [
            {"name": f"User{i}", "email": f"user{i}@batch.com", "age": 20 + i}
            for i in range(1, 11)
        ]
    }

    response = requests.post(f"{BASE_URL}/api/users/batch", json=batch_users)
    if response.status_code == 201:
        result = response.json()
        print(f"Batch inserted {result['inserted']} users")

def demo_metrics():
    """Metrics collection"""
    print("\n=== Metrics Collection ===\n")

    # Send some metrics
    metrics = [
        {"name": "cpu_usage", "value": 45.2},
        {"name": "cpu_usage", "value": 52.1},
        {"name": "cpu_usage", "value": 48.7},
        {"name": "memory_usage", "value": 1024.5},
        {"name": "memory_usage", "value": 1156.3},
        {"name": "requests_per_sec", "value": 1250}
    ]

    for metric in metrics:
        response = requests.post(f"{BASE_URL}/api/metrics", json=metric)
        if response.status_code == 201:
            print(f"Recorded metric: {metric['name']} = {metric['value']}")
        time.sleep(0.1)  # Small delay between metrics

    # Get metrics
    response = requests.get(f"{BASE_URL}/api/metrics/cpu_usage", params={"limit": 5})
    cpu_metrics = response.json()
    print(f"\nLatest CPU usage metrics: {len(cpu_metrics)} entries")
    for metric in cpu_metrics[:3]:
        print(f"  {metric['value']} at timestamp {metric['timestamp']}")

def demo_performance():
    """Performance testing"""
    print("\n=== Performance Test ===\n")

    # Measure write performance
    start_time = time.time()
    for i in range(100):
        requests.post(f"{BASE_URL}/api/users", json={
            "name": f"PerfUser{i}",
            "email": f"perf{i}@test.com",
            "age": 25
        })
    write_time = time.time() - start_time
    print(f"100 writes in {write_time:.3f} seconds")
    print(f"Write throughput: {100/write_time:.0f} ops/sec")

    # Measure read performance
    start_time = time.time()
    for i in range(100):
        requests.get(f"{BASE_URL}/api/users")
    read_time = time.time() - start_time
    print(f"\n100 reads in {read_time:.3f} seconds")
    print(f"Read throughput: {100/read_time:.0f} ops/sec")

def demo_stats():
    """Database statistics"""
    print("\n=== Database Statistics ===\n")

    response = requests.get(f"{BASE_URL}/api/stats")
    stats = response.json()

    print(f"Users count: {stats['users_count']}")
    print(f"Sessions count: {stats['sessions_count']}")
    print(f"Metrics count: {stats['metrics_count']}")
    print(f"Memory used: {stats['memory']['used'] / 1024 / 1024:.2f} MB")
    print(f"Memory size: {stats['memory']['size'] / 1024 / 1024:.2f} MB")
    print(f"Uptime: {stats['uptime']:.2f} seconds")

def main():
    print("==================================================")
    print("Tarantool HTTP Server Example")
    print("==================================================\n")

    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("Server is ready!\n")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"Waiting for server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("Error: Cannot connect to Tarantool HTTP server")
                print("Make sure the server is running on port 8080")
                return

    try:
        demo_health_check()
        demo_user_crud()
        demo_batch_operations()
        demo_metrics()
        demo_performance()
        demo_stats()

        print("\n==================================================")
        print("Tarantool HTTP Server: REST API with In-Memory DB")
        print("\nKey features demonstrated:")
        print("• RESTful API with JSON")
        print("• CRUD operations")
        print("• Batch operations")
        print("• Metrics collection")
        print("• High-performance in-memory storage")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Tarantool HTTP server is running:")
        print("docker build -t tarantool-http .")
        print("docker run -d -p 8080:8080 -p 3301:3301 tarantool-http")

if __name__ == "__main__":
    main()