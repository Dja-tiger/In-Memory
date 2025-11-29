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

# Clean previous run
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "${CONTAINER_NAME}" > /dev/null
fi

echo "Starting Tarantool with dialog_app.lua..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p 3301:3301 \
  -v "${SCRIPT_DIR}/dialog_app.lua:/opt/tarantool/init.lua:ro" \
  tarantool/tarantool:latest > /dev/null

sleep 4

if [ ! -d "${SCRIPT_DIR}/venv" ]; then
  python3 -m venv "${SCRIPT_DIR}/venv"
fi
source "${SCRIPT_DIR}/venv/bin/activate"
pip install -q --upgrade pip tarantool

python3 "${SCRIPT_DIR}/dialog_benchmark.py"

echo
read -p "Keep the Tarantool dialog container running? (y/N): " -r ANSWER
if [[ ! $ANSWER =~ ^[Yy]$ ]]; then
  docker rm -f "${CONTAINER_NAME}" > /dev/null
fi

deactivate
