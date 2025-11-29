-- Dialog service implemented as Tarantool stored procedures
-- Provides message append, retrieval, and stats via call API

local fiber = require('fiber')

box.cfg{
    listen = '0.0.0.0:3301',
    memtx_memory = 256 * 1024 * 1024,
}

-- One-time bootstrap: spaces, indexes, users, and sequences
box.once('dialog_migration', function()
    -- Users for demos and automation
    box.schema.user.create('app', {password = 'pass', if_not_exists = true})
    box.schema.user.grant('app', 'read,write,execute', 'universe', {if_not_exists = true})
    box.schema.user.grant('guest', 'read,write,execute', 'universe', {if_not_exists = true})

    local dialogs = box.schema.space.create('dialogs', {
        if_not_exists = true,
        format = {
            {name = 'dialog_id', type = 'unsigned'},
            {name = 'message_id', type = 'unsigned'},
            {name = 'author', type = 'string'},
            {name = 'body', type = 'string'},
            {name = 'created_at', type = 'number'},
        },
    })

    dialogs:create_index('primary', {
        if_not_exists = true,
        parts = {
            {field = 'dialog_id', type = 'unsigned'},
            {field = 'message_id', type = 'unsigned'},
        },
    })

    dialogs:create_index('by_dialog_time', {
        if_not_exists = true,
        unique = false,
        parts = {
            {field = 'dialog_id', type = 'unsigned'},
            {field = 'created_at', type = 'number'},
        },
    })

    box.schema.sequence.create('message_seq', {if_not_exists = true, min = 1})
end)

local function to_message(tuple)
    return {
        dialog_id = tuple.dialog_id,
        message_id = tuple.message_id,
        author = tuple.author,
        body = tuple.body,
        created_at = tuple.created_at,
    }
end

function add_message(dialog_id, author, body)
    if body == nil or body == '' then
        return {error = 'message body is required'}
    end

    local message_id = box.sequence.message_seq:next()
    local created_at = fiber.time()

    local inserted = box.space.dialogs:put({
        dialog_id or 0,
        message_id,
        author or 'anonymous',
        body,
        created_at,
    })

    return to_message(inserted)
end

function get_dialog(dialog_id, limit)
    limit = limit or 50
    local tuples = box.space.dialogs.index.by_dialog_time:select({dialog_id or 0}, {
        iterator = 'EQ',
        limit = limit,
    })

    local messages = {}
    for _, tuple in ipairs(tuples) do
        table.insert(messages, to_message(tuple))
    end

    return messages
end

function dialog_stats(dialog_id)
    local total = box.space.dialogs.index.primary:count(dialog_id or 0)
    local last = box.space.dialogs.index.by_dialog_time:max({dialog_id or 0})

    return {
        dialog_id = dialog_id or 0,
        messages = total,
        last_at = last and last.created_at or nil,
    }
end

-- Register functions for remote execution
for _, func in ipairs({'add_message', 'get_dialog', 'dialog_stats'}) do
    box.schema.func.create(func, {if_not_exists = true})
    box.schema.user.grant('guest', 'execute', 'function', func, {if_not_exists = true})
    box.schema.user.grant('app', 'execute', 'function', func, {if_not_exists = true})
end

return true
