#!/bin/bash

set -euo pipefail

echo "===================================="
echo "   Tarantool Dialog UDF showcase"
echo "===================================="

if ! command -v docker &> /dev/null; then
  echo "Docker is required"
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
CONTAINER_NAME="tarantool-dialogs"

# отдельный venv именно под этот проект
VENV_DIR="${SCRIPT_DIR}/.venv_dialogs"
VENV_PYTHON="${VENV_DIR}/bin/python3"

# Чистим предыдущий контейнер
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "${CONTAINER_NAME}" > /dev/null
fi

echo "Starting Tarantool 2.11 with dialog_app.lua..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p 3301:3301 \
  -v "${SCRIPT_DIR}/dialog_app.lua:/opt/tarantool/init.lua:ro" \
  --entrypoint tarantool \
  tarantool/tarantool:2.11 \
  /opt/tarantool/init.lua > /dev/null

# даём серверу время подняться и выполнить init.lua
sleep 4

# пересоздаём venv, чтобы не ловить старый мусор
rm -rf "${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

# проверяем, что python3 в venv реально существует
if [ ! -x "${VENV_PYTHON}" ]; then
  echo "Python3 inside venv not found at ${VENV_PYTHON}"
  exit 1
fi

# ставим зависимости через python из venv
"${VENV_PYTHON}" -m pip install -q --upgrade pip tarantool

# запускаем бенчмарк, явно передавая пользователя app/pass
"${VENV_PYTHON}" "${SCRIPT_DIR}/dialog_benchmark.py" \
  --user app \
  --password pass

echo
read -p "Keep the Tarantool dialog container running? (y/N): " -r ANSWER
if [[ ! $ANSWER =~ ^[Yy]$ ]]; then
  docker rm -f "${CONTAINER_NAME}" > /dev/null
fi
