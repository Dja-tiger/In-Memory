# Примеры Tarantool

Tarantool - это мощная платформа вычислений в памяти, объединяющая возможности базы данных и сервера приложений.

## 📁 Файлы

- `example.py` - Базовые операции Tarantool (спейсы, Lua процедуры, файберы, очереди)
- `http_example.py` - Пример REST API с HTTP сервером
- `app.lua` - Tarantool приложение с HTTP сервером
- `Dockerfile` - Пользовательский образ с модулем HTTP сервера
- `run.sh` - Запуск базового примера
- `run_http.sh` - Запуск примера HTTP сервера

## 🚀 Быстрый старт

### Базовый пример
```bash
./run.sh
```

### Пример HTTP сервера
```bash
./run_http.sh
```

## 🌟 Демонстрируемые возможности

### Базовый пример (`example.py`)
- **Спейсы и кортежи**: NoSQL модель данных
- **Lua процедуры**: Серверная логика
- **Файберы**: Легковесные корутины для конкурентности
- **Очереди сообщений**: Встроенная функциональность очередей
- **Высокая производительность**: ~31K ops/sec

### Пример HTTP сервера (`http_example.py`)
- **REST API**: Полные CRUD операции
- **Пакетные операции**: Массовые вставки
- **Сбор метрик**: Данные временных рядов
- **Статистика БД**: Мониторинг в реальном времени
- **Высокая производительность**: ~400-500 ops/sec через HTTP

### Модуль диалогов (домашнее задание)
- **Хранимые процедуры**: `add_message`, `get_dialog`, `dialog_stats`
- **Перенос логики в UDF**: работа только через `box.call`
- **Нагрузочное тестирование**: сравнение SQLite → Tarantool
- **Автоматический старт**: `./run_dialogs.sh`

## 🔧 Tarantool Console

Connect to running instance:
```bash
# Basic instance
docker exec -it tarantool-demo tarantoolctl connect localhost:3301

# HTTP server instance
docker exec -it tarantool-http tarantoolctl connect localhost:3301
```

Common commands:
```lua
-- List all spaces
box.space._space:select()

-- Insert data
box.space.users:insert{1, 'Alice', 'alice@example.com'}

-- Query data
box.space.users:select()

-- Execute Lua
box.execute("SELECT * FROM users")
```

## 🌐 HTTP API Endpoints

When running the HTTP server example:

### Health Check
```bash
curl http://localhost:8080/health
```

### Users API
```bash
# Get all users
curl http://localhost:8080/api/users

# Create user
curl -X POST http://localhost:8080/api/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","age":30}'

# Get user by ID
curl http://localhost:8080/api/users/1

# Update user
curl -X PUT http://localhost:8080/api/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"age":31}'

# Delete user
curl -X DELETE http://localhost:8080/api/users/1

# Search users
curl "http://localhost:8080/api/users/search?email=example.com"

# Batch insert
curl -X POST http://localhost:8080/api/users/batch \
  -H 'Content-Type: application/json' \
  -d '{"users":[{"name":"Bob","email":"bob@test.com"},{"name":"Charlie","email":"charlie@test.com"}]}'
```

### Metrics API
```bash
# Send metric
curl -X POST http://localhost:8080/api/metrics \
  -H 'Content-Type: application/json' \
  -d '{"name":"cpu_usage","value":45.2}'

# Get metrics by name
curl http://localhost:8080/api/metrics/cpu_usage
```

### Statistics
```bash
curl http://localhost:8080/api/stats
```

## 🧑‍💻 Домашнее задание: перенос модуля в Tarantool

В каталоге лежит готовый пример миграции модуля «диалоги» в Tarantool с вынесением логики в хранимые процедуры Lua.

### Файлы

- `dialog_app.lua` — определение спейса `dialogs` и UDF `add_message`, `get_dialog`, `dialog_stats`
- `dialog_benchmark.py` — скрипт, сравнивающий базовый SQL (SQLite) и Tarantool-вариант
- `run_dialogs.sh` — запускает Tarantool c `dialog_app.lua` и проводит нагрузочный тест

### Быстрый старт

```bash
cd tarantool
./run_dialogs.sh
```

Скрипт поднимет контейнер Tarantool, установит Python-зависимости и выведет метрики до/после миграции.


### Как выполнить домашнее задание целиком

1. **Поставьте зависимости**: нужен Docker (для контейнера Tarantool) и Python 3.10+ с `pip` (для бенчмарка). Внутренняя база SQLite встроена и дополнительных сервисов не требует.
2. **Запустите автоматический сценарий**: перейдите в каталог `tarantool` и выполните `./run_dialogs.sh`. Скрипт:
   - стартует контейнер Tarantool с `dialog_app.lua`,
   - устанавливает Python-зависимости в изолированную папку `.venv_dialogs`,
   - прогоняет нагрузочный тест `dialog_benchmark.py` для SQLite и Tarantool, печатает QPS/latency.
3. **Сохраните результаты**: в выводе будет два блока `=== SQLite baseline ===` и `=== Tarantool dialogs ===` с цифрами на вставку/чтение. Скопируйте эти показатели для отчёта «до/после».
4. **Покажите UDF-вызовы**: в коде теста используются только вызовы `box.call` к функциям `add_message`, `get_dialog`, `dialog_stats` — это подтверждает перенос логики в хранимые процедуры.
5. **Оформите сдачу**: приложите ссылку на репозиторий, укажите команды запуска (`cd tarantool && ./run_dialogs.sh`) и добавьте в README или отчёт полученные метрики.



```lua
-- Добавить сообщение и вернуть созданную запись
box.call('add_message', {dialog_id, author, body})

-- Получить последние N сообщений диалога
box.call('get_dialog', {dialog_id, limit})

-- Статистика по диалогу (кол-во сообщений, последняя активность)
box.call('dialog_stats', {dialog_id})
```

### Сравнение производительности

`dialog_benchmark.py` последовательно прогоняет два стора:

1. **SQLite** — базовый вариант без in-memory UDF
2. **Tarantool** — логика вынесена в Lua, доступ только через `call`

На выходе вы увидите QPS на запись/чтение и медианную задержку на вставку. Так можно зафиксировать эффект от миграции.

## 🏗️ Building Custom Image

The HTTP server example uses a custom Docker image with the HTTP module:

```bash
# Build image
docker build -t tarantool-http .

# Run container
docker run -d --name tarantool-http \
  -p 8080:8080 \
  -p 3301:3301 \
  tarantool-http
```

## 📊 Performance Characteristics

| Operation | Performance | Notes |
|-----------|------------|-------|
| Basic Operations | ~31K ops/sec | Direct connection |
| HTTP Writes | ~400 ops/sec | REST API |
| HTTP Reads | ~500 ops/sec | REST API |
| Memory Usage | <1MB overhead | Efficient memory management |
| Startup Time | <1 second | Fast initialization |

## 🔍 Key Concepts

### Spaces
Tarantool's equivalent of tables:
- Schema-less or with format
- Multiple indexes (TREE, HASH, BITSET, RTREE)
- ACID transactions

### Fibers
Lightweight coroutines:
- Cooperative multitasking
- Thousands of concurrent fibers
- No thread overhead

### Lua Integration
- Stored procedures
- Triggers
- Custom business logic
- Hot code reload

### HTTP Server
- Built-in HTTP/1.1 server
- WebSocket support
- JSON API
- Middleware support

## 🆚 Comparison with Redis

| Feature | Tarantool | Redis |
|---------|-----------|-------|
| Data Model | Tuples/Documents | Key-Value |
| Query Language | SQL + Lua | Commands |
| ACID Transactions | ✅ Full | ⚠️ Limited |
| Stored Procedures | ✅ Lua | ✅ Lua scripts |
| HTTP API | ✅ Built-in | ❌ Needs proxy |
| Clustering | ✅ Built-in | ✅ Redis Cluster |
| Performance | Very High | Very High |

## 📝 Notes

- Tarantool combines database and application server
- Excellent for stateful microservices
- Supports both SQL and NoSQL operations
- Production-ready with enterprise features
- Active open-source community

## 🔗 Resources

- [Official Documentation](https://www.tarantool.io/en/doc/)
- [Lua Reference](https://www.tarantool.io/en/doc/latest/reference/reference_lua/)
- [HTTP Module](https://github.com/tarantool/http)
- [Docker Hub](https://hub.docker.com/r/tarantool/tarantool)