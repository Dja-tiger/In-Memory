# Примеры Valkey

## Обзор
Valkey - это высокопроизводительное хранилище данных типа ключ-значение с открытым исходным кодом. Это форк Redis, созданный сообществом после изменения лицензии Redis на SSPLv1 и RSALv2. Valkey поддерживает 100% совместимость с протоколом Redis, добавляя улучшения производительности.

## Ключевые особенности
- **Лицензия BSD 3-Clause** - По-настоящему открытый исходный код
- **Совместимость с протоколом Redis** - Используйте существующие клиенты и инструменты Redis
- **Многопоточный ввод-вывод** - Лучшая производительность на многоядерных системах
- **Улучшенная производительность** - До 37% быстрее Redis 7.2
- **Управление сообществом** - Открытая модель управления

## Предварительные требования
- Docker
- Python 3.6+
- Инструменты Redis CLI (работают с Valkey)

## Быстрый старт
```bash
./run.sh
```

## Ручная настройка

### 1. Запуск Valkey
```bash
# Используя Docker (рекомендуется)
docker run -d -p 6379:6379 --name valkey valkey/valkey:latest

# С пользовательской конфигурацией
docker run -d -p 6379:6379 --name valkey valkey/valkey:latest \
    valkey-server \
    --io-threads 4 \
    --io-threads-do-reads yes

# Сборка из исходников
git clone https://github.com/valkey-io/valkey.git
cd valkey
make
./src/valkey-server
```

### 2. Установка зависимостей Python
```bash
# Valkey использует протокол Redis, поэтому redis-py работает
pip install redis
```

### 3. Запуск примера
```bash
python3 example.py
```

## Протокол Valkey (RESP - Такой же как Redis)

Valkey использует точно такой же протокол, как Redis (RESP). Подключение через telnet:

```bash
telnet localhost 6379
```

Все команды Redis работают идентично в Valkey. См. README Redis для подробных примеров протокола.

### Быстрый тест протокола
```bash
# Тест соединения
echo "PING" | nc localhost 6379
+PONG

# Установка и получение значения
(echo "*3"; echo "\$3"; echo "SET"; echo "\$5"; echo "mykey"; echo "\$7"; echo "myvalue") | nc localhost 6379
+OK

(echo "*2"; echo "\$3"; echo "GET"; echo "\$5"; echo "mykey") | nc localhost 6379
$7
myvalue
```

## Оптимизации производительности

### Многопоточный ввод-вывод
Valkey реализует многопоточный ввод-вывод для лучшей производительности на современных многоядерных системах:

```bash
# Настройка потоков ввода-вывода (через CLI)
CONFIG SET io-threads 4
CONFIG SET io-threads-do-reads yes

# Или при запуске
valkey-server --io-threads 4 --io-threads-do-reads yes
```

### Сравнение бенчмарков
```bash
# Бенчмарк Valkey
docker run --rm --network host valkey/valkey valkey-benchmark -h localhost -p 6379

# Сравнение с Redis (если работает на другом порту)
redis-benchmark -h localhost -p 6379 -t set,get -n 1000000 -P 16 -q

# Результаты (типичные):
# Valkey:  999,800 запросов/сек
# Redis 7: 729,400 запросов/сек
```

## Миграция с Redis

### 1. Миграция данных
```bash
# Valkey использует тот же формат RDB/AOF что и Redis

# Вариант 1: Использовать существующую директорию данных Redis
valkey-server /path/to/redis/dir/redis.conf

# Вариант 2: Использовать BGSAVE и восстановить
# На Redis:
redis-cli BGSAVE

# Скопировать dump.rdb в директорию данных Valkey
cp /var/lib/redis/dump.rdb /var/lib/valkey/

# Запустить Valkey - он загрузит файл RDB
valkey-server
```

### 2. Миграция через репликацию
```bash
# Установить Valkey как реплику существующего Redis
valkey-cli REPLICAOF redis-host 6379

# После завершения синхронизации, повысить до основного
valkey-cli REPLICAOF NO ONE
```

### 3. Миграция клиента
```python
# Изменения кода не требуются!
# Просто укажите на экземпляр Valkey

import redis

# Работает с Redis
r = redis.Redis(host='redis-server', port=6379)

# Также работает с Valkey (идентичное API)
r = redis.Redis(host='valkey-server', port=6379)
```

## Различия в конфигурации

Большинство конфигураций Redis работают без изменений. Специфичные для Valkey оптимизации:

```conf
# valkey.conf

# Многопоточность (улучшение Valkey)
io-threads 4
io-threads-do-reads yes

# Все стандартные конфигурации Redis работают
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1 300 10 60 10000
appendonly yes
```

## Мониторинг

### Использование команды INFO
```bash
# Информация о сервере
echo "INFO server" | nc localhost 6379

# Статистика памяти
echo "INFO memory" | nc localhost 6379

# Статистика производительности
echo "INFO stats" | nc localhost 6379

# Все секции
echo "INFO all" | nc localhost 6379
```

### Ключевые метрики для мониторинга
```bash
# Через telnet
telnet localhost 6379

INFO stats
# Обратите внимание на:
# - instantaneous_ops_per_sec
# - total_commands_processed
# - rejected_connections
# - keyspace_hits/misses

INFO memory
# Обратите внимание на:
# - used_memory_human
# - mem_fragmentation_ratio
# - evicted_keys

INFO cpu
# Обратите внимание на:
# - used_cpu_sys
# - used_cpu_user
```

## Кластеризация

Valkey поддерживает протокол Redis Cluster с улучшениями:

### Запуск кластера
```bash
# Создание 6 узлов (3 основных, 3 реплики)
for port in 7000 7001 7002 7003 7004 7005; do
    mkdir -p cluster/${port}
    cat > cluster/${port}/valkey.conf <<EOF
port ${port}
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
EOF
    valkey-server cluster/${port}/valkey.conf &
done

# Создание кластера
valkey-cli --cluster create \
    127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
    127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
    --cluster-replicas 1
```

### Команды кластера
```bash
# Информация о кластере
CLUSTER INFO

# Список узлов
CLUSTER NODES

# Проверка слотов
CLUSTER SLOTS

# Ручная отработка отказа
CLUSTER FAILOVER
```

## Настройка производительности

### 1. Оптимизация памяти
```bash
# Установка максимальной памяти
CONFIG SET maxmemory 2gb

# Выбор политики вытеснения
CONFIG SET maxmemory-policy volatile-lru

# Включение сжатия
CONFIG SET hash-max-ziplist-entries 512
CONFIG SET hash-max-ziplist-value 64
```

### 2. Оптимизация сети
```bash
# TCP backlog
CONFIG SET tcp-backlog 511

# Keep alive
CONFIG SET tcp-keepalive 300

# Отключение медленных клиентов
CONFIG SET timeout 300
```

### 3. Настройка персистентности
```bash
# Настройки RDB
CONFIG SET save "900 1 300 10 60 10000"

# Настройки AOF
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec
CONFIG SET no-appendfsync-on-rewrite yes
```

## Безопасность

### Аутентификация
```bash
# Установка пароля
CONFIG SET requirepass mypassword

# Подключение с паролем
valkey-cli -a mypassword

# Или аутентификация после подключения
AUTH mypassword
```

### ACL (Списки контроля доступа)
```bash
# Создание пользователя
ACL SETUSER alice on >password ~cached:* +get +set

# Список пользователей
ACL LIST

# Проверка разрешений
ACL WHOAMI
```

## Преимущества над Redis

1. **Лицензия**: BSD 3-Clause (по-настоящему открытый исходный код)
2. **Производительность**: Лучшее использование многоядерности
3. **Сообщество**: Открытое управление, прозрачная разработка
4. **Совместимость**: 100% совместимость с протоколом Redis
5. **Инновации**: Более быстрый цикл разработки функций

## Типичные варианты использования

Те же, что и Redis:
- Кэширование
- Хранение сессий
- Аналитика в реальном времени
- Очереди сообщений
- Таблицы лидеров
- Ограничение скорости

Улучшено для:
- Сценариев с высокой пропускной способностью
- Многоядерных систем
- Облачных развёртываний

## Устранение неполадок

### Проблемы с подключением
```bash
# Проверка работы Valkey
ps aux | grep valkey

# Тест соединения
valkey-cli ping

# Проверка логов
docker logs valkey-demo
```

### Проблемы с производительностью
```bash
# Проверка медленных запросов
valkey-cli SLOWLOG GET 10

# Мониторинг команд
valkey-cli MONITOR

# Проверка задержки
valkey-cli --latency
```

### Проблемы с памятью
```bash
# Статистика памяти
valkey-cli INFO memory

# Поиск больших ключей
valkey-cli --bigkeys

# Диагностика памяти
valkey-cli MEMORY DOCTOR
```

## Ресурсы

- [Valkey GitHub](https://github.com/valkey-io/valkey)
- [Документация Valkey](https://valkey.io/docs/)
- [Руководство по миграции](https://valkey.io/docs/migration/)
- [Бенчмарки производительности](https://valkey.io/benchmarks/)