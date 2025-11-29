#!/usr/bin/env tarantool

-- Tarantool HTTP Server Example
-- This demonstrates REST API with in-memory database

local http_server = require('http.server')
local json = require('json')
local fiber = require('fiber')

-- Configure database
box.cfg{
    listen = 3301,
    memtx_memory = 256 * 1024 * 1024, -- 256MB
}

-- Create spaces if not exists
if not box.space.users then
    local users = box.schema.space.create('users')
    users:format({
        {name = 'id', type = 'unsigned'},
        {name = 'name', type = 'string'},
        {name = 'email', type = 'string'},
        {name = 'age', type = 'unsigned'},
        {name = 'created_at', type = 'unsigned'},
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

if not box.space.sessions then
    local sessions = box.schema.space.create('sessions')
    sessions:format({
        {name = 'token', type = 'string'},
        {name = 'user_id', type = 'unsigned'},
        {name = 'created_at', type = 'unsigned'},
        {name = 'expires_at', type = 'unsigned'},
    })
    sessions:create_index('primary', {
        type = 'hash',
        parts = {'token'}
    })
end

if not box.space.metrics then
    local metrics = box.schema.space.create('metrics')
    metrics:format({
        {name = 'id', type = 'unsigned'},
        {name = 'name', type = 'string'},
        {name = 'value', type = 'number'},
        {name = 'timestamp', type = 'unsigned'},
    })
    metrics:create_index('primary', {
        type = 'tree',
        parts = {'id'}
    })
    metrics:create_index('name_time', {
        type = 'tree',
        parts = {'name', 'timestamp'}
    })
end

-- Counter for auto-increment IDs
local counter = {
    users = 0,
    metrics = 0
}

-- Initialize counters
for _, user in box.space.users:pairs() do
    if user.id > counter.users then
        counter.users = user.id
    end
end

for _, metric in box.space.metrics:pairs() do
    if metric.id > counter.metrics then
        counter.metrics = metric.id
    end
end

-- Create HTTP server
local httpd = http_server.new('0.0.0.0', 8080, {
    log_requests = true,
    log_errors = true
})

-- Helper functions
local function json_response(req, data, status)
    local resp = req:render({json = data})
    resp.status = status or 200
    return resp
end

local function error_response(req, message, status)
    return json_response(req, {error = message}, status or 400)
end

-- Track startup time
local start_time = fiber.time()

-- Routes

-- Health check
httpd:route({path = '/health'}, function(req)
    return json_response(req, {
        status = 'healthy',
        uptime = fiber.time() - start_time,
        memory = box.slab.info().arena_used,
        version = _TARANTOOL
    })
end)

-- Get all users
httpd:route({path = '/api/users', method = 'GET'}, function(req)
    local users = {}
    for _, user in box.space.users:pairs() do
        table.insert(users, {
            id = user.id,
            name = user.name,
            email = user.email,
            age = user.age,
            created_at = user.created_at
        })
    end
    return json_response(req, users)
end)

-- Get user by ID
httpd:route({path = '/api/users/:id', method = 'GET'}, function(req)
    local id = tonumber(req:stash('id'))
    if not id then
        return error_response(req, 'Invalid user ID', 400)
    end

    local user = box.space.users:get(id)
    if not user then
        return error_response(req, 'User not found', 404)
    end

    return json_response(req, {
        id = user.id,
        name = user.name,
        email = user.email,
        age = user.age,
        created_at = user.created_at
    })
end)

-- Create user
httpd:route({path = '/api/users', method = 'POST'}, function(req)
    local body = req:json()
    if not body or not body.name or not body.email then
        return error_response(req, 'Name and email are required', 400)
    end

    -- Check if email already exists
    local existing = box.space.users.index.email:get(body.email)
    if existing then
        return error_response(req, 'Email already exists', 409)
    end

    counter.users = counter.users + 1
    local user = box.space.users:insert{
        counter.users,
        body.name,
        body.email,
        body.age or 0,
        fiber.time()
    }

    return json_response(req, {
        id = user.id,
        name = user.name,
        email = user.email,
        age = user.age,
        created_at = user.created_at
    }, 201)
end)

-- Update user
httpd:route({path = '/api/users/:id', method = 'PUT'}, function(req)
    local id = tonumber(req:stash('id'))
    if not id then
        return error_response(req, 'Invalid user ID', 400)
    end

    local body = req:json()
    if not body then
        return error_response(req, 'Invalid request body', 400)
    end

    local user = box.space.users:get(id)
    if not user then
        return error_response(req, 'User not found', 404)
    end

    -- Check email uniqueness if changing
    if body.email and body.email ~= user.email then
        local existing = box.space.users.index.email:get(body.email)
        if existing then
            return error_response(req, 'Email already exists', 409)
        end
    end

    user = box.space.users:update(id, {
        {'=', 2, body.name or user.name},
        {'=', 3, body.email or user.email},
        {'=', 4, body.age or user.age}
    })

    return json_response(req, {
        id = user.id,
        name = user.name,
        email = user.email,
        age = user.age,
        created_at = user.created_at
    })
end)

-- Delete user
httpd:route({path = '/api/users/:id', method = 'DELETE'}, function(req)
    local id = tonumber(req:stash('id'))
    if not id then
        return error_response(req, 'Invalid user ID', 400)
    end

    local user = box.space.users:get(id)
    if not user then
        return error_response(req, 'User not found', 404)
    end

    box.space.users:delete(id)
    return json_response(req, {message = 'User deleted'})
end)

-- Search users by email pattern
httpd:route({path = '/api/users/search', method = 'GET'}, function(req)
    local email_pattern = req:query_param('email')
    if not email_pattern then
        return error_response(req, 'Email parameter required', 400)
    end

    local users = {}
    for _, user in box.space.users:pairs() do
        if string.find(user.email, email_pattern) then
            table.insert(users, {
                id = user.id,
                name = user.name,
                email = user.email,
                age = user.age,
                created_at = user.created_at
            })
        end
    end

    return json_response(req, users)
end)

-- Metrics endpoint
httpd:route({path = '/api/metrics', method = 'POST'}, function(req)
    local body = req:json()
    if not body or not body.name or not body.value then
        return error_response(req, 'Name and value are required', 400)
    end

    counter.metrics = counter.metrics + 1
    local metric = box.space.metrics:insert{
        counter.metrics,
        body.name,
        body.value,
        fiber.time()
    }

    return json_response(req, {
        id = metric.id,
        name = metric.name,
        value = metric.value,
        timestamp = metric.timestamp
    }, 201)
end)

-- Get metrics by name
httpd:route({path = '/api/metrics/:name', method = 'GET'}, function(req)
    local name = req:stash('name')
    local limit = tonumber(req:query_param('limit')) or 100

    local metrics = {}
    for _, metric in box.space.metrics.index.name_time:pairs({name}, {iterator = 'REQ'}) do
        if metric.name ~= name then break end
        table.insert(metrics, {
            id = metric.id,
            name = metric.name,
            value = metric.value,
            timestamp = metric.timestamp
        })
        if #metrics >= limit then break end
    end

    return json_response(req, metrics)
end)

-- Database stats
httpd:route({path = '/api/stats', method = 'GET'}, function(req)
    local stats = {
        users_count = box.space.users:count(),
        sessions_count = box.space.sessions:count(),
        metrics_count = box.space.metrics:count(),
        memory = {
            used = box.slab.info().arena_used,
            size = box.slab.info().arena_size
        },
        uptime = fiber.time() - start_time
    }
    return json_response(req, stats)
end)

-- Batch insert example
httpd:route({path = '/api/users/batch', method = 'POST'}, function(req)
    local body = req:json()
    if not body or not body.users or type(body.users) ~= 'table' then
        return error_response(req, 'Users array required', 400)
    end

    local inserted = {}
    box.begin()
    for _, user_data in ipairs(body.users) do
        if user_data.name and user_data.email then
            -- Check if email exists
            local existing = box.space.users.index.email:get(user_data.email)
            if not existing then
                counter.users = counter.users + 1
                local user = box.space.users:insert{
                    counter.users,
                    user_data.name,
                    user_data.email,
                    user_data.age or 0,
                    fiber.time()
                }
                table.insert(inserted, {
                    id = user.id,
                    name = user.name,
                    email = user.email
                })
            end
        end
    end
    box.commit()

    return json_response(req, {
        inserted = #inserted,
        users = inserted
    }, 201)
end)

-- Start the server
httpd:start()

print('Tarantool HTTP server started on port 8080')
print('API endpoints:')
print('  GET    /health')
print('  GET    /api/users')
print('  GET    /api/users/:id')
print('  POST   /api/users')
print('  PUT    /api/users/:id')
print('  DELETE /api/users/:id')
print('  GET    /api/users/search?email=pattern')
print('  POST   /api/users/batch')
print('  POST   /api/metrics')
print('  GET    /api/metrics/:name')
print('  GET    /api/stats')

-- Keep the server running
require('console').start()