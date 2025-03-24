#!/bin/bash

# Путь к проекту
PROJECT_DIR="/root/company_new_server"
PROJECT_LOGS_DIR="/root/company_new_server/logs"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"

# Имена программ для Supervisor
SERVER_NAME="company_server"
WORKER_NAME="company_worker"

# Установка зависимостей системы
echo "Установка системных зависимостей..."
apt-get update
apt-get install -y python3 python3-venv python3-pip supervisor

# Создание виртуального окружения, если его нет
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
fi

# Активация виртуального окружения и установка зависимостей
echo "Установка зависимостей проекта..."
"$PIP" install -r "$PROJECT_DIR/requirements.txt"

# Установка pydantic-settings, если не указан в requirements.txt
"$PIP" install pydantic-settings

# Создание директории для конфигураций Supervisor, если её нет
SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"
if [ ! -d "$SUPERVISOR_CONF_DIR" ]; then
    echo "Создание директории $SUPERVISOR_CONF_DIR..."
    mkdir -p "$SUPERVISOR_CONF_DIR"
fi

# Создание конфигурационного файла для сервера (main.py)
echo "Создание конфигурации для $SERVER_NAME..."
cat <<EOT > "$SUPERVISOR_CONF_DIR/$SERVER_NAME.conf"
[program:$SERVER_NAME]
command=$VENV_DIR/bin/uvicorn main:app --host 0.0.0.0 --port 8000
directory=$PROJECT_DIR
autostart=true
autorestart=true
startretries=3
stderr_logfile=$PROJECT_LOGS_DIR/$SERVER_NAME.err.log
stdout_logfile=$PROJECT_LOGS_DIR/$SERVER_NAME.out.log
environment=PATH="$VENV_DIR/bin:%(ENV_PATH)s"
EOT

# Создание конфигурационного файла для воркера (worker.py)
echo "Создание конфигурации для $WORKER_NAME..."
cat <<EOT > "$SUPERVISOR_CONF_DIR/$WORKER_NAME.conf"
[program:$WORKER_NAME]
command=$PYTHON $PROJECT_DIR/worker.py
directory=$PROJECT_DIR
autostart=true
autorestart=true
startretries=3
stderr_logfile=$PROJECT_LOGS_DIR/$WORKER_NAME.err.log
stdout_logfile=$PROJECT_LOGS_DIR/$WORKER_NAME.out.log
environment=PATH="$VENV_DIR/bin:%(ENV_PATH)s"
EOT

# Обновление конфигурации Supervisor
echo "Обновление конфигурации Supervisor..."
supervisorctl reread
supervisorctl update

# Запуск всех программ
echo "Запуск сервера и воркера..."
supervisorctl start all

# Проверка статуса
echo "Проверка статуса процессов..."
supervisorctl status

echo "Настройка и запуск завершены!"
