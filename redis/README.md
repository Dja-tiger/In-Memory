# Примеры Redis

## Обзор
Redis - это хранилище структур данных в памяти с открытым исходным кодом, используемое как база данных, кэш и брокер сообщений. Поддерживает различные структуры данных, включая строки, хеши, списки, множества, упорядоченные множества, битовые карты, гиперлоглоги и геопространственные индексы.

Эта директория содержит примеры для:
- **Standalone Redis** - Операции с одним экземпляром
- **Redis Cluster** - Распределённая установка с шардингом

## Предварительные требования
- Docker
- Python 3.6+
- telnet или netcat для тестирования протокола

## Быстрый старт

### Standalone Redis
```bash
# Запуск примера с standalone Redis
./run.sh
```

### Redis Cluster
```bash
# 1. Настройка кластера (создаёт 6 узлов: 3 мастера + 3 реплики)
./setup_cluster.sh

# 2. Запуск примеров кластера
python3 example_cluster.py

# 3. Остановка кластера после завершения
./stop_cluster.sh
```

## Ручная настройка

### 1. Запуск Redis
```bash
# Используя Docker
docker run -d -p 6379:6379 --name redis redis:latest

# Или установка локально
# Ubuntu/Debian
sudo apt-get install redis-server

# MacOS
brew install redis
redis-server
```

### 2. Установка зависимостей Python
```bash
pip install redis
```

### 3. Запуск примера
```bash
python3 example.py
```

## Протокол Redis (RESP - REdis Serialization Protocol)

Redis использует протокол RESP. Подключение через telnet:

```bash
telnet localhost 6379
```

### Формат RESP

Протокол Redis использует эти префиксы:
- `+` Простые строки
- `-` Ошибки
- `:` Целые числа
- `$` Массивные строки
- `*` Массивы

### Основные команды через Telnet

#### Операции со строками

```bash
# PING - Тест соединения
PING
+PONG

# SET key value
*3
$3
SET
$5
mykey
$7
myvalue
+OK

# GET key
*2
$3
GET
$5
mykey
$7
myvalue

# SET с истечением срока (EX = секунды)
*5
$3
SET
$5
mykey
$7
myvalue
$2
EX
$2
60
+OK

# INCR - Увеличить число
*2
$4
INCR
$7
counter
:1

# MSET - Установить несколько ключей
*7
$4
MSET
$4
key1
$6
value1
$4
key2
$6
value2
$4
key3
$6
value3
+OK
```

#### Операции со списками

```bash
# LPUSH - Добавить слева
*3
$5
LPUSH
$6
mylist
$5
item1
:1

# RPUSH - Добавить справа
*3
$5
RPUSH
$6
mylist
$5
item2
:2

# LRANGE - Получить диапазон
*4
$6
LRANGE
$6
mylist
$1
0
$2
-1
*2
$5
item1
$5
item2

# LPOP - Извлечь слева
*2
$4
LPOP
$6
mylist
$5
item1
```

#### Операции с множествами

```bash
# SADD - Добавить в множество
*3
$4
SADD
$5
myset
$7
member1
:1

# SMEMBERS - Получить все элементы
*2
$8
SMEMBERS
$5
myset
*1
$7
member1

# SISMEMBER - Проверка принадлежности
*3
$9
SISMEMBER
$5
myset
$7
member1
:1
```

#### Операции с хешами

```bash
# HSET - Установить поле хеша
*4
$4
HSET
$6
user:1
$4
name
$5
Alice
:1

# HGET - Получить поле хеша
*3
$4
HGET
$6
user:1
$4
name
$5
Alice

# HGETALL - Получить все поля
*2
$7
HGETALL
$6
user:1
*2
$4
name
$5
Alice
```

#### Операции с упорядоченными множествами

```bash
# ZADD - Добавить с оценкой
*4
$4
ZADD
$11
leaderboard
$3
100
$7
player1
:1

# ZRANGE с оценками
*5
$6
ZRANGE
$11
leaderboard
$1
0
$2
-1
$10
WITHSCORES
*2
$7
player1
$3
100
```

### Pub/Sub через Telnet

#### Терминал 1 - Подписчик
```bash
telnet localhost 6379

# Подписаться на канал
*2
$9
SUBSCRIBE
$7
channel1
*3
$9
subscribe
$7
channel1
:1

# Вы будете получать сообщения здесь
*3
$7
message
$7
channel1
$11
Hello World
```

#### Терминал 2 - Публикатор
```bash
telnet localhost 6379

# Опубликовать сообщение
*3
$7
PUBLISH
$7
channel1
$11
Hello World
:1
```

### Транзакции

```bash
# Начать транзакцию
MULTI
+OK

# Команды в очереди
SET key1 value1
+QUEUED

SET key2 value2
+QUEUED

# Выполнить
EXEC
*2
+OK
+OK
```

### Lua скрипты

```bash
# EVAL скрипт numkeys key1 arg1
*5
$4
EVAL
$35
return redis.call('get', KEYS[1])
$1
1
$5
mykey
$7
myvalue

# Более сложный скрипт
EVAL "return {KEYS[1],ARGV[1]}" 1 key value
*2
$3
key
$5
value
```

## Расширенные возможности Redis

### Конфигурация персистентности

```bash
# Проверка статуса персистентности
INFO persistence

# Запустить ручное сохранение
BGSAVE
+Background saving started

# Синхронное сохранение (блокирует сервер!)
SAVE
+OK

# Настроить AOF
CONFIG SET appendonly yes
+OK
```

### Управление памятью

```bash
# Получить информацию о памяти
INFO memory

# Установить максимальную память
CONFIG SET maxmemory 100mb
+OK

# Установить политику вытеснения
CONFIG SET maxmemory-policy allkeys-lru
+OK

# Использование памяти ключа
MEMORY USAGE mykey
:58
```

### Мониторинг

```bash
# Мониторинг всех команд в реальном времени
MONITOR
+OK
1234567890.123456 [0 127.0.0.1:12345] "SET" "key" "value"

# Получить медленные запросы
SLOWLOG GET 10

# Сбросить лог медленных запросов
SLOWLOG RESET
+OK

# Список клиентов
CLIENT LIST
id=3 addr=127.0.0.1:12345 fd=6 name= age=10 ...

# Статистика команд
INFO commandstats
```

## Тестирование производительности

### Использование redis-cli
```bash
# Бенчмарк с redis-benchmark
docker run --rm --network host redis redis-benchmark -h localhost -p 6379

# Определённые тесты
redis-benchmark -t set,get -n 100000 -q

# Режим конвейера
redis-benchmark -P 16 -n 100000

# Пользовательская команда
redis-benchmark -n 100000 LRANGE mylist 0 99
```

### Использование telnet для массовых операций
```bash
# Генерация массовых команд
for i in {1..1000}; do
    echo -e "*3\r\n\$3\r\nSET\r\n\$5\r\nkey$i\r\n\$5\r\nvalue\r\n"
done | nc localhost 6379
```

## Примеры типов данных Redis

### 1. Строки
- Токены сессий
- Счётчики
- Кэшированные значения

### 2. Списки
- Очереди сообщений
- Ленты активности
- Очереди задач

### 3. Множества
- Теги
- Уникальные посетители
- Списки друзей

### 4. Упорядоченные множества
- Таблицы лидеров
- Очереди с приоритетом
- Данные временных рядов

### 5. Хеши
- Профили пользователей
- Хранение объектов
- Конфигурация

### 6. Потоки
- Событийное источниковедение
- Очередь сообщений
- Логи аудита

### 7. Битовые карты
- Отслеживание активности пользователей
- Флаги функций
- Фильтры Блума

### 8. HyperLogLog
- Подсчёт уникальных посетителей
- Оценка мощности

### 9. Геопространственные
- Поиск по местоположению
- Ближайшие точки
- Вычисления расстояний

## Типичные паттерны

### 1. Паттерн Cache-Aside
```python
def get_user(user_id):
    user = redis.get(f"user:{user_id}")
    if not user:
        user = db.query(user_id)
        redis.setex(f"user:{user_id}", 3600, user)
    return user
```

### 2. Паттерн Write-Through
```python
def save_user(user_id, data):
    redis.set(f"user:{user_id}", data)
    db.save(user_id, data)
```

### 3. Распределённая блокировка
```bash
# Получить блокировку с таймаутом
SET lock:resource unique_value NX EX 10
+OK

# Освободить блокировку (сначала проверить значение)
EVAL "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end" 1 lock:resource unique_value
:1
```

## Лучшие практики

1. **Именование ключей**: Используйте двоеточия для пространств имён (например, `user:1000:profile`)
2. **Стратегия TTL**: Всегда устанавливайте TTL для ключей кэша
3. **Пул соединений**: Переиспользуйте соединения
4. **Операции конвейера**: Пакетная обработка команд для производительности
5. **Лимиты памяти**: Настройте maxmemory и политику вытеснения
6. **Персистентность**: Используйте RDB и AOF для критичных данных
7. **Мониторинг**: Отслеживайте память, команды и медленные запросы

## Устранение неполадок

### Проблемы с подключением
```bash
# Тест соединения
redis-cli ping

# Проверка работы Redis
ps aux | grep redis

# Проверка порта
netstat -an | grep 6379
```

### Проблемы с памятью
```bash
# Проверка использования памяти
redis-cli INFO memory

# Найти большие ключи
redis-cli --bigkeys

# Примеры ключей
redis-cli --memkeys
```

### Проблемы с производительностью
```bash
# Проверка лога медленных запросов
redis-cli SLOWLOG GET 10

# Мониторинг команд
redis-cli MONITOR

# Проверка подключённых клиентов
redis-cli CLIENT LIST

# Проверка статистики команд
redis-cli INFO commandstats
```

## Redis Cluster

### Ручная настройка кластера

Если автоматический скрипт настройки не работает, вот как создать кластер вручную:

```bash
# 1. Запустить 6 узлов Redis
for port in 7000 7001 7002 7003 7004 7005; do
    docker run -d \
        --name redis-node-$port \
        --net redis-cluster-net \
        -p $port:$port \
        redis:latest \
        redis-server --port $port --cluster-enabled yes \
        --cluster-config-file nodes.conf \
        --cluster-node-timeout 5000 \
        --protected-mode no \
        --bind 0.0.0.0
done

# 2. Получить IP адреса контейнеров
for port in 7000 7001 7002 7003 7004 7005; do
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis-node-$port
done

# 3. Создать кластер (замените IP на реальные значения)
docker exec redis-node-7000 redis-cli --cluster create \
    IP1:7000 IP2:7001 IP3:7002 IP4:7003 IP5:7004 IP6:7005 \
    --cluster-replicas 1

# Введите 'yes' при запросе

# 4. Проверить кластер
docker exec redis-node-7000 redis-cli -p 7000 cluster info
docker exec redis-node-7000 redis-cli -p 7000 cluster nodes
```

### Тестирование кластера с CLI

```bash
# Подключиться к кластеру (обратите внимание на флаг -c для режима кластера)
docker exec -it redis-node-7000 redis-cli -c -p 7000

# Тест шардинга - ключи будут перенаправлены на соответствующие узлы
127.0.0.1:7000> SET key1 value1
-> Redirected to slot [9189] located at 192.168.97.3:7001
OK

127.0.0.1:7001> SET key2 value2
-> Redirected to slot [4998] located at 192.168.97.2:7000
OK

# Хеш-теги гарантируют попадание ключей в один слот
127.0.0.1:7000> SET {user:123}:profile "Alice"
OK
127.0.0.1:7000> SET {user:123}:settings "dark_mode"
OK
127.0.0.1:7000> MGET {user:123}:profile {user:123}:settings
1) "Alice"
2) "dark_mode"
```

### Команды кластера

```bash
# Информация о кластере
CLUSTER INFO

# Список всех узлов
CLUSTER NODES

# Показать назначения слотов
CLUSTER SLOTS

# Получить слот ключа
CLUSTER KEYSLOT mykey

# Подсчитать ключи в слоте
CLUSTER COUNTKEYSINSLOT 5460

# Ручное переключение при отказе
CLUSTER FAILOVER
```

### Пример кластера на Python

```python
from redis.cluster import RedisCluster, ClusterNode

# Определить начальные узлы
startup_nodes = [
    ClusterNode("localhost", 7000),
    ClusterNode("localhost", 7001),
    ClusterNode("localhost", 7002)
]

# Подключиться к кластеру
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# Операции работают прозрачно
rc.set("key1", "value1")  # Автоматически направляется на правильный узел
value = rc.get("key1")

# Хеш-теги для многоключевых операций
rc.mset({
    "{user:1}:name": "Alice",
    "{user:1}:age": "30"
})
```

## Заметки по безопасности

1. **Привязка**: Привязывайтесь только к определённым интерфейсам
2. **Пароль**: Всегда используйте requirepass в продакшене
3. **Команды**: Отключите опасные команды (FLUSHDB, CONFIG и т.д.)
4. **Защищённый режим**: Оставляйте включённым в продакшене
5. **TLS**: Используйте TLS для шифрованных соединений

```bash
# Установить пароль
CONFIG SET requirepass mypassword
+OK

# Аутентифицироваться
AUTH mypassword
+OK
```