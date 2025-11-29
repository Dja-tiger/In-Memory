#!/usr/bin/env tarantool

-- Dialog service implemented as Tarantool stored procedures
-- Provides message append, retrieval, and stats via call API

local fiber = require('fiber')

-- Базовая конфигурация Tarantool
box.cfg{
    listen = '0.0.0.0:3301',
    memtx_memory = 256 * 1024 * 1024, -- 256MB
}

----------------------------------------------------------------------
-- Пользователи и права
----------------------------------------------------------------------

-- Создаём пользователя app с паролем pass (если ещё не создан)
box.schema.user.create('app', {password = 'pass', if_not_exists = true})

-- Права app на всю "вселенную"
pcall(function()
    box.schema.user.grant('app', 'read,write,execute', 'universe')
end)

-- Права guest на всю "вселенную"
pcall(function()
    box.schema.user.grant('guest', 'read,write,execute', 'universe')
end)

----------------------------------------------------------------------
-- One-time bootstrap: space, индексы, sequence
----------------------------------------------------------------------

box.once('dialog_migration', function()
    -- основное хранилище сообщений диалогов
    local dialogs = box.schema.space.create('dialogs', {
        if_not_exists = true,
        format = {
            {name = 'dialog_id',  type = 'unsigned'},
            {name = 'message_id', type = 'unsigned'},
            {name = 'author',     type = 'string'},
            {name = 'body',       type = 'string'},
            {name = 'created_at', type = 'number'}, -- UNIX time (fiber.time)
        },
    })

    -- primary индекс по (dialog_id, message_id)
    dialogs:create_index('primary', {
        if_not_exists = true,
        parts = {
            {field = 'dialog_id',  type = 'unsigned'},
            {field = 'message_id', type = 'unsigned'},
        },
    })

    -- индекс для выборки по времени внутри диалога
    dialogs:create_index('by_dialog_time', {
        if_not_exists = true,
        unique = false,
        parts = {
            {field = 'dialog_id',  type = 'unsigned'},
            {field = 'created_at', type = 'number'},
        },
    })

    -- глобальный sequence для message_id
    box.schema.sequence.create('message_seq', {
        if_not_exists = true,
        min = 1,
    })
end)

----------------------------------------------------------------------
-- Утилита для преобразования tuple -> Lua-таблица
----------------------------------------------------------------------

local function to_message(tuple)
    return {
        dialog_id  = tuple.dialog_id,
        message_id = tuple.message_id,
        author     = tuple.author,
        body       = tuple.body,
        created_at = tuple.created_at,
    }
end

----------------------------------------------------------------------
-- UDF-функции (вызываются через box.call)
----------------------------------------------------------------------

-- Добавление сообщения в диалог
function add_message(dialog_id, author, body)
    if body == nil or body == '' then
        return { error = 'message body is required' }
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

-- Получение последних сообщений диалога
function get_dialog(dialog_id, limit)
    limit = limit or 50

    local tuples = box.space.dialogs.index.by_dialog_time:select(
        { dialog_id or 0 },
        { iterator = 'EQ', limit = limit }
    )

    local messages = {}
    for _, tuple in ipairs(tuples) do
        table.insert(messages, to_message(tuple))
    end

    return messages
end

-- Статистика по диалогу
function dialog_stats(dialog_id)
    dialog_id = dialog_id or 0

    local total = box.space.dialogs.index.primary:count(dialog_id)
    local last  = box.space.dialogs.index.by_dialog_time:max({ dialog_id })

    return {
        dialog_id = dialog_id,
        messages  = total,
        last_at   = last and last.created_at or nil,
    }
end

----------------------------------------------------------------------
-- Регистрация функций как UDF и grant execute
----------------------------------------------------------------------

for _, func_name in ipairs({'add_message', 'get_dialog', 'dialog_stats'}) do
    -- регистрируем функцию в _func
    box.schema.func.create(func_name, { if_not_exists = true })

    -- даём право execute пользователю app
    pcall(function()
        box.schema.user.grant('app', 'execute', 'function', func_name)
    end)

    -- даём право execute пользователю guest
    pcall(function()
        box.schema.user.grant('guest', 'execute', 'function', func_name)
    end)
end

return true
