#!/usr/bin/env python3
"""
Tarantool example - In-memory computing platform with Lua
"""

import tarantool
import time
import json

# Connect to Tarantool
conn = tarantool.connect("localhost", 3301, user="guest")

def demo_spaces_and_tuples():
    """Demonstrate spaces (tables) and tuples"""
    print("=== Tarantool Spaces & Tuples ===\n")

    # Create space (table) if not exists
    try:
        # Using Lua to create space
        conn.eval("""
            if not box.space.users then
                local users = box.schema.space.create('users')
                users:format({
                    {name = 'id', type = 'unsigned'},
                    {name = 'name', type = 'string'},
                    {name = 'email', type = 'string'}
                })
                users:create_index('primary', {
                    type = 'tree',
                    parts = {'id'}
                })
                users:create_index('email', {
                    type = 'hash',
                    parts = {'email'},
                    unique = true
                })
            end
            return true
        """)
        print("Created 'users' space with indexes")
    except:
        print("Space 'users' already exists")

    # Insert data
    space = conn.space('users')
    space.replace((1, 'Alice', 'alice@example.com'))
    space.replace((2, 'Bob', 'bob@example.com'))
    print("Inserted users")

    # Select data
    users = space.select()
    print(f"All users: {users}")

    # Select by index
    user = space.select(1)
    print(f"User with id=1: {user}")

def demo_transactions():
    """ACID transactions with MVCC"""
    print("\n=== ACID Transactions ===\n")

    result = conn.eval("""
        box.begin()

        -- Transaction operations
        local space = box.space.users
        space:update(1, {{'+', 1, 1}})  -- Would fail due to type
        space:replace{3, 'Charlie', 'charlie@example.com'}

        box.commit()
        return "Transaction completed"
    """)
    print(f"Transaction result: {result}")

def demo_lua_procedures():
    """Stored procedures in Lua"""
    print("\n=== Lua Stored Procedures ===\n")

    # Define procedure
    conn.eval("""
        function get_user_by_email(email)
            local space = box.space.users
            local index = space.index.email
            return index:select(email)
        end

        function increment_counter(key, value)
            local space = box.space._schema
            local tuple = space:get(key)
            if tuple == nil then
                space:replace{key, value}
                return value
            else
                local new_value = tuple[2] + value
                space:replace{key, new_value}
                return new_value
            end
        end
    """)

    # Call procedure
    result = conn.call('get_user_by_email', ['alice@example.com'])
    print(f"User by email: {result}")

def demo_fibers():
    """Cooperative multitasking with fibers"""
    print("\n=== Fibers (Coroutines) ===\n")

    fiber_code = """
        local fiber = require('fiber')

        -- Create fibers
        local results = {}

        local function worker(name, delay)
            fiber.sleep(delay)
            table.insert(results, name .. " completed")
        end

        -- Start multiple fibers
        fiber.create(worker, "Fiber1", 0.1)
        fiber.create(worker, "Fiber2", 0.05)
        fiber.create(worker, "Fiber3", 0.15)

        -- Wait for completion
        fiber.sleep(0.2)

        return results
    """

    results = conn.eval(fiber_code)
    print(f"Fiber results: {results}")

def demo_queues():
    """Message queue functionality"""
    print("\n=== Message Queues ===\n")

    # Create queue space
    conn.eval("""
        if not box.space.queue then
            local queue = box.schema.space.create('queue')
            queue:format({
                {name = 'id', type = 'unsigned'},
                {name = 'status', type = 'string'},
                {name = 'data', type = 'string'}
            })
            queue:create_index('primary', {parts = {'id'}})
            queue:create_index('status', {parts = {'status'}, unique = false})
        end
    """)

    # Queue operations
    conn.eval("""
        function enqueue(data)
            local queue = box.space.queue
            local id = queue:len() + 1
            queue:insert{id, 'pending', data}
            return id
        end

        function dequeue()
            local queue = box.space.queue
            local task = queue.index.status:select('pending', {limit = 1})
            if #task > 0 then
                queue:update(task[1][1], {{'=', 2, 'processing'}})
                return task[1]
            end
            return nil
        end
    """)

    # Use queue
    for i in range(3):
        conn.call('enqueue', [f'Task {i+1}'])

    print("Enqueued 3 tasks")

    task = conn.call('dequeue')
    print(f"Dequeued task: {task}")

def demo_performance():
    """Performance benchmarking"""
    print("\n=== Performance Demo ===\n")

    # Bulk insert
    start = time.time()

    conn.eval("""
        if not box.space.benchmark then
            local bench = box.schema.space.create('benchmark')
            bench:create_index('primary')
        end

        local space = box.space.benchmark
        space:truncate()

        for i = 1, 10000 do
            space:insert{i, 'data_' .. tostring(i)}
        end

        return space:len()
    """)

    elapsed = time.time() - start
    print(f"Inserted 10,000 records in {elapsed:.3f} seconds")
    print(f"Throughput: {10000/elapsed:.0f} ops/sec")

if __name__ == "__main__":
    try:
        # Test connection
        conn.ping()
        print("Connected to Tarantool!\n")
        print("=" * 50 + "\n")

        demo_spaces_and_tuples()
        demo_lua_procedures()
        demo_fibers()
        demo_queues()
        demo_performance()

        print("\n" + "=" * 50)
        print("Tarantool: In-Memory Computing Platform")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Tarantool is running:")
        print("docker run -d -p 3301:3301 --name tarantool tarantool/tarantool")