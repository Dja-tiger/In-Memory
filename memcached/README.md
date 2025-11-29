# Примеры Memcached

## Обзор
Memcached - это высокопроизводительная распределённая система кэширования объектов в памяти. Использует простую модель хранения ключ-значение.

## Предварительные требования
- Docker
- Python 3.6+
- netcat (nc) для тестирования

## Быстрый старт
```bash
./run.sh
```

## Ручная настройка

### 1. Запуск Memcached
```bash
# Используя Docker
docker run -d -p 11211:11211 --name memcached memcached:latest

# Или установка локально
# Ubuntu/Debian
sudo apt-get install memcached

# MacOS
brew install memcached
memcached -p 11211 -m 64 -vv
```

### 2. Установка зависимостей Python
```bash
pip install pymemcache
```

### 3. Запуск примера
```bash
python3 example.py
```

## Протокол Memcached (Telnet)

Memcached использует простой текстовый протокол. Подключение через telnet:

```bash
telnet localhost 11211
```

### Основные команды

#### Команды хранения

```bash
# SET - Сохранение данных
set key 0 60 5
hello
STORED

# Параметры:
# key: имя ключа
# 0: флаги (произвольное целое число)
# 60: время истечения в секундах (0 = никогда)
# 5: количество байт в блоке данных

# GET - Получение данных
get key
VALUE key 0 5
hello
END

# ADD - Сохранить только если ключ не существует
add newkey 0 60 5
world
STORED

# REPLACE - Сохранить только если ключ существует
replace key 0 60 5
world
STORED

# APPEND - Добавить данные к существующему ключу
append key 0 60 5
_more
STORED

# PREPEND - Добавить данные в начало существующего ключа
prepend key 0 60 5
start_
STORED

# DELETE - Удалить ключ
delete key
DELETED
```

#### Команды извлечения

```bash
# GET нескольких ключей
get key1 key2 key3
VALUE key1 0 5
data1
VALUE key2 0 5
data2
END

# GETS - Получение с токеном CAS (Compare-And-Swap)
gets key
VALUE key 0 5 12345
hello
END
# 12345 - уникальный идентификатор CAS

# CAS - Проверка и установка
cas key 0 60 5 12345
world
STORED
```

#### Числовые команды

```bash
# Установка начального значения
set counter 0 0 2
10
STORED

# INCR - Увеличение
incr counter 5
15

# DECR - Уменьшение
decr counter 3
12
```

#### Статистика

```bash
# Получить всю статистику
stats
STAT pid 1234
STAT uptime 3600
STAT time 1234567890
STAT version 1.6.9
STAT curr_connections 10
STAT total_connections 100
STAT cmd_get 1000
STAT cmd_set 500
STAT get_hits 900
STAT get_misses 100
STAT bytes 12345
STAT curr_items 50
END

# Получить определенную группу статистики
stats slabs
stats items
stats sizes

# Сброс статистики
stats reset
RESET
```

#### Другие команды

```bash
# FLUSH_ALL - Очистить все данные
flush_all
OK

# FLUSH_ALL с задержкой (секунды)
flush_all 60
OK

# VERSION - Получить версию сервера
version
VERSION 1.6.9

# QUIT - Закрыть соединение
quit
```

### Продвинутые примеры протокола

#### Многострочный SET
```bash
# Сохранение JSON данных
set user:1 0 60 50
{"id":1,"name":"Alice","email":"alice@example.com"}
STORED
```

#### Пакетные операции
```bash
# Можно выполнять команды конвейером без ожидания ответов
set key1 0 60 5
data1
set key2 0 60 5
data2
set key3 0 60 5
data3
STORED
STORED
STORED
```

#### Использование флагов
```bash
# Флаги могут указывать тип данных или сжатие
# 0 = обычная строка
# 1 = JSON
# 2 = сжатые данные
set data 2 60 100
<сжатые_данные_здесь>
STORED

get data
VALUE data 2 100
<сжатые_данные_здесь>
END
```

## Тестирование производительности

### Использование telnet для базового бенчмарка
```bash
# Простой тест в bash цикле
for i in {1..1000}; do
    echo -e "set key$i 0 60 5\r\nvalue\r\n" | nc localhost 11211
done
```

### Использование memcached-tool
```bash
# Установка memcached-tool
# Обычно включена в пакет с memcached

# Отображение слабов
memcached-tool localhost:11211 display

# Отображение статистики
memcached-tool localhost:11211 stats

# Дамп всех ключей (если включено)
memcached-tool localhost:11211 dump
```

## Типичные варианты использования

1. **Хранение сессий**: Хранение пользовательских сессий с автоматическим истечением
2. **Кэш запросов к БД**: Кэширование дорогих запросов к базе данных
3. **Кэш ответов API**: Кэширование ответов сторонних API
4. **Кэш фрагментов страниц**: Кэширование отрендеренных HTML фрагментов
5. **Кэш объектов**: Кэширование сериализованных объектов

## Мониторинг

Мониторинг производительности Memcached:
```bash
# Просмотр статистики в реальном времени
watch -n 1 'echo stats | nc localhost 11211'

# Мониторинг соотношения get/set
echo stats | nc localhost 11211 | grep -E "cmd_get|cmd_set|get_hits|get_misses"
```

## Ограничения

- Максимальная длина ключа: 250 байт
- Максимальный размер значения: 1МБ (по умолчанию)
- Нет персистентности - данные теряются при перезапуске
- Нет встроенной безопасности/аутентификации (используйте SASL в продакшене)
- Нет типов данных кроме байтов
- LRU вытеснение при заполнении памяти

## Лучшие практики

1. **Именование ключей**: Используйте согласованные префиксы (например, `user:123`, `session:abc`)
2. **Стратегия TTL**: Устанавливайте подходящее время истечения
3. **Пул соединений**: Переиспользуйте соединения в продакшене
4. **Мониторинг**: Отслеживайте соотношение попаданий/промахов (стремитесь к >90% попаданий)
5. **Управление памятью**: Мониторьте частоту вытеснений
6. **Согласованное хеширование**: Используйте для распределённых установок

## Устранение неполадок

### Отказ в соединении
```bash
# Проверка работы Memcached
ps aux | grep memcached

# Проверка порта
netstat -an | grep 11211

# Тест соединения
nc -zv localhost 11211
```

### Высокая частота вытеснений
```bash
# Проверка использования памяти
echo stats | nc localhost 11211 | grep -E "limit_maxbytes|bytes"

# Увеличение лимита памяти
memcached -m 128 -p 11211
```

### Режим отладки
```bash
# Запуск с подробным выводом
memcached -vv

# Запуск с очень подробным выводом
memcached -vvv
```