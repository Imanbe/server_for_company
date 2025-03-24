# Carex Task Distribution System

## Описание проекта

`Company Task Distribution System` — это асинхронное приложение на Python, предназначенное для распределения сделок между сотрудниками Битрикс24 с использованием базы данных SQLite, очередей Redis и интеграции с Bitrix24 через вебхуки. Проект включает мониторинг с помощью Prometheus, логирование и обработку ошибок.

Основные функции:
- Распределение сделок между доступными пользователями с использованием случайного выбора.
- Хранение пользователей в SQLite с поддержкой исключения (exclusion).
- Очереди задач в Redis с обработкой ошибок.
- Интеграция с Bitrix24 для выполнения задач.
- Логирование в два файла: основные события и отладочная информация.
- Метрики Prometheus для мониторинга обработки задач и ошибок.

Оффтоп:
- Проект подразумевает собой пример сервера для обслуживания разных задач, в данном случае для расширения функционала портала Битрикс24
- Проект можно использовать как шаблон, когда для какой-то компании нужен сервер с обслуживанием

## Требования

- `Python 3.10+`
- `Redis` (локально или удалённо)
- `SQLite` (встроен в Python)
- Установленные зависимости из `requirements.txt`

## Установка

### Автоматический способ:
1. **Настройте переменные окружения:**
   - Создайте файл `.env` в корне проекта и добавьте необходимые настройки (см. `Configs/config.py`):
   ```env
    REDIS_URL=redis://:Password@localhost:6379/0
    WEBHOOK_CAREX=https://bitrix24.ru/rest/<user_id>/<secret_key>/
    ```

2. **Инициализируйте базу данных:**
    ```bash
    python -m src.BD.init_db
    ```

3. **Настройте и запустите скрипт:**
    ```bash
   chmod +x src/Scripts/setup_supervisor.sh
   bash src/Scripts/setup_supervisor.sh
    ```
- Скрипт использует supervisorctl с настройками автоматиечского перезапуска в случае падения
- Скриншот настроек скрипта:
![Скриншот настройки скрипта](materials\ScriptSettings.png) 

### Ручной способ:
1. **Клонируйте репозиторий:**
    ```bash
    git clone <repository_url>
    cd carex_task_distribution
    ```

2. **Создайте виртуальное окружение:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\\Scripts\\activate     # Windows
    ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
    ```

4. **Настройте переменные окружения:**
   - Создайте файл `.env` в корне проекта и добавьте необходимые настройки (см. `Configs/config.py`):
   ```env
    REDIS_URL=redis://:Password@localhost:6379/0
    WEBHOOK_CAREX=https://bitrix24.ru/rest/<user_id>/<secret_key>/
    ```

5. **Инициализируйте базу данных:**
    ```bash
    python -m src.BD.init_db
    ```

## Структура проекта

## Использование

### Запуск приложения

1. **Запустите воркер:**
   ```bash
    python -m src.Workers.worker
    ```
2. **Запустите FastAPI сервер:**
   ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```
3. **Просмотр базы данных:**
    ```bash
    python -m src.BD.view\n
   ```

### Основные эндпоинты

- **POST /CarexRandom**
- Параметры: `deal_id: int`, `cont_id: int`
- Описание: Добавляет задачу в очередь для распределения.
- Пример:
  ```bash
  - curl -X POST "http://localhost:8000/CompanyRandom?deal_id=123&cont_id=456"
  ```

- **GET /retry-errors**
- Описание: Повторно обрабатывает задачи из очереди ошибок.
- Пример:
    ```bash
    curl -X GET "http://localhost:8000/retry-errors"
    ```
- **GET /metrics**
- Описание: Просмотр метрик Prometheus.

### Просмотр пользователей
- Используйте скрипт `view.py` для интерактивного просмотра пользователей в базе данных:
    ```bash
    python -m src.BD.view
    ```
- Команды:
- `1` — Показать всех пользователей.
- `2` — Показать только доступных пользователей.
- `3` — Выход.

## Логирование
- `company_main.log` — основные события приложения (INFO и выше).
- `company_debug.log` — отладочная информация (DEBUG и выше).

## Метрики Prometheus
Доступны по адресу `/metrics`. Основные метрики:
- `company_tasks_processed_total` — общее количество обработанных задач.
- `company_task_processing_time_second` — время обработки задач.
- `company_tasks_in_queue` — количество задач в очереди.
- `company_tasks_in_queue_errors` — количество задач в очереди ошибок.
- `company_redis_errors_total` — ошибки Redis.
- `company_bitrix_errors_total` — ошибки Bitrix API.

## Обработка ошибок
- Задачи, завершившиеся с ошибкой, перемещаются в очередь `task_random_error_queue`.
- Эндпоинт `/retry-errors` позволяет повторно обработать эти задачи.

## Разработка
Для добавления новых типов задач:
1. Пропишите в `configs.TaskTypes` название нового метода, который будет обрабатывать задачу
2. Создайте эндпоинт по образцу из `src/main.py`, в переменной `task_type` поменяйте значение на новый созданный из `settings.TaskTypes`
3. Создайте обработчик в `src/Handlers/` (пример: `process_company_random.py`).
4. Главный метод обработчике импортируйте `src/Handlers/handlers.py` (пример: `src\Handlers\handlers.py`)
5. Добавьте его в `settings.HANDLERS` в `Configs/config.py`.
6. В файле `src\Configs\config.py` есть более подробное описание


## Лицензия
`MIT License`
