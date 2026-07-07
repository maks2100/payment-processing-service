# payment-processing-service

Сервис для обработки платежей. Построен на FastAPI с использованием асинхронной базы данных PostgreSQL и брокера сообщений RabbitMQ. Реализует Outbox pattern для гарантированной доставки сообщений.

## Архитектура

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   API        │────>│   RabbitMQ   │────>│   Consumer   │
│   Service    │     │  (Rabbit)    │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘
        │                                       │
        v                                       v
  ┌──────────────┐                     ┌──────────────┐
  │   PostgreSQL │                     │  Outbox      │
  │   (payments, │<───────────────────│  /Handled    │
  │    outbox)   │     Dual-Write     │  Events      │
  └──────────────┘                    └──────────────┘
```

- **API Service** — принимает запросы на создание платежей, сохраняет их в БД и записывает в outbox
- **Consumer Service** — читает из outbox, публикует сообщения в RabbitMQ, фиксирует в handled_events
- **Outbox pattern** — гарантирует, что каждое платежное событие будет доставлено хотя бы раз

## Базовая конфигурация

Проект использует файловую конфигурацию через `.env`. Конфигурация находится в [`app/src/core/config.py`](app/src/core/config.py).

### Переменные окружения

Для корректной работы необходимо задать следующие переменные:

#### Основные

| Переменная | Описание | По умолчанию |
|---|---|---|
| `ENVIRONMENT` | Окружение: `local`, `dev`, `production` | `production` |
| `APP_NAME` | Название приложения | `Payment Processing Service` |
| `APP_VERSION` | Версия приложения | `VERSION NOT SET` |
| `API_PREFIX` | Префикс API маршрутов | `/api/v1` |

#### База данных (PostgreSQL)

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DB__HOST` | Адрес сервера PostgreSQL | — |
| `DB__PORT` | Порт PostgreSQL | `5432` |
| `DB__USER` | Имя пользователя | — |
| `DB__PASSWORD` | Пароль | — |
| `DB__DATABASE` | Имя базы данных | — |
| `DB_POOL_SIZE` | Размер пула соединений | `5` |
| `DB_POOL_MAX_OVERFLOW` | Максимум переполнений пула | `10` |
| `DB_POOL_TIMEOUT` | Таймаут получения соединения (сек) | `30` |
| `DB_POOL_RECYCLE` | Время жизни соединения (сек) | `3600` |

> **Примечание:** Переменные для подключения к БД используют префикс `DB__` (двойное подчёркивание) для поддержки вложенных настроек pydantic-settings.

#### CORS и доверенные хосты

| Переменная | Описание | По умолчанию |
|---|---|---|
| `CORS_ALLOW_ORIGINS` | Список разрешённых origins (через запятую) | `[]` |
| `CORS_ALLOW_CREDENTIALS` | Разрешить cookies | `False` |
| `CORS_ALLOW_METHODS` | Разрешённые HTTP методы | `GET,POST,PATCH,DELETE,OPTIONS` |
| `CORS_ALLOW_HEADERS` | Разрешённые заголовки | `Authorization,Content-Type` |
| `TRUSTED_HOSTS` | Доверенные хосты (через запятую) | `[]` |

> **Примечание:** При `ENVIRONMENT=local` настройки CORS автоматически расширяются до `*`, а `TRUSTED_HOSTS` устанавливается в `*`.

#### RabbitMQ

| Переменная | Описание | По умолчанию |
|---|---|---|
| `INCLUDE_CONSUMER` | Включить consumer service | `false` |

## Локальный запуск

### Требования

- Python >= 3.12, < 3.13
- Docker и Docker Compose

### Быстрый запуск (Docker Compose)

```bash
# 1. Скопируйте файл окружения
cp .build/local/.env.example .build/local/.env

# 2. Настройте переменные в .build/local/.env
#    Заполните DB__USER, DB__PASSWORD, DB__DATABASE, DB_PORT_EXPOSE, API_KEY

# 3. Запустите все сервисы
cd .build/local
docker compose up -d

# 4. Запустите миграции
docker compose exec api uv run alembic upgrade head
```

Сервисы будут доступны:
- **API**: [`http://localhost:8000/api/v1`](http://localhost:8000/api/v1)
- **Swagger UI**: [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs)
- **RabbitMQ Management**: [`http://localhost:15672`](http://localhost:15672) (логин/пароль: `guest`/`guest`)

### Локальный запуск (без Docker)

#### Требования

- PostgreSQL (локально)
- RabbitMQ (локально)

#### Установка

1. Перейдите в директорию приложения:

```bash
cd app
```

2. Установите зависимости (используется `uv`):

```bash
uv sync
```

3. Создайте файл `.env` в директории `app/`:

```bash
cp .env.example .env  # если есть шаблон
# или создайте вручную:
```

4. Заполните `.env` необходимыми значениями. Пример для локальной разработки:

```env
ENVIRONMENT=local
APP_NAME=Payment Processing Service
APP_VERSION=0.1.0
API_PREFIX=/api/v1

DB__HOST=localhost
DB__PORT=5432
DB__USER=postgres
DB__PASSWORD=postgres
DB__DATABASE=payment_processing

CORS_ALLOW_ORIGINS=*
TRUSTED_HOSTS=*

API_KEY=your-secret-api-key
```

#### Запуск

##### С помощью uvicorn:

```bash
cd app
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

##### С помощью fastapi dev:

```bash
cd app
uv run fastapi dev src/main.py
```

API будет доступен по адресу: `http://localhost:8000/api/v1`

- Swagger UI (документация): `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Запуск consumer service

Consumer service обрабатывает сообщения из RabbitMQ и фиксирует события в handled_events.

```bash
# В Docker
cd .build/local
INCLUDE_CONSUMER=true docker compose up -d consumer

# Локально
cd app
INCLUDE_CONSUMER=true uv run uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Миграции базы данных (Alembic)

```bash
cd app

# Создание новой миграции
uv run alembic revision --autogenerate -m "description"

# Применение миграций
uv run alembic upgrade head

# Откат последней миграции
uv run alembic downgrade -1

# Проверка текущей версии
uv run alembic current
```

## Структура проекта

```
app/
├── pyproject.toml              # Зависимости и конфигурация
├── alembic.ini                 # Конфигурация Alembic
├── migrations/                 # Миграции базы данных
│   ├── env.py
│   └── versions/
│       ├── 2026_07_02_1237-05af1698644d_... (payments)
│       ├── 2026_07_03_0853-8e8c90f1e17e_... (outbox)
│       └── 2026_07_03_1030-8a50dffcdfb8_... (handled_events)
└── src/
    ├── __init__.py
    ├── main.py                 # Точка входа (FastAPI приложение)
    └── core/
        ├── config.py           # Настройки и конфигурация
        ├── enums.py            # Перечисления
        ├── events.py           # События жизненного цикла
        ├── exceptions.py       # Исключения
        ├── exception_handlers.py  # Обработчики ошибок
        ├── logging.py          # Настройка логирования
        ├── middleware.py       # Middleware
        ├── responses.py        # Форматы ответов
        ├── routes.py           # Маршрутизация
        ├── dependencies.py     # Dependency injection
        ├── clients.py          # Клиенты внешних сервисов
        ├── broker/             # RabbitMQ брокер и роутер
        │   ├── __init__.py
        │   └── rabbit.py
        └── db/                 # Конфигурация базы данных
            ├── __init__.py
            ├── base.py
            └── manager.py
    ├── payments/               # Payment domain
    │   ├── models.py           # ORM модели
    │   ├── schemas.py          # Pydantic схемы
    │   ├── services.py         # Бизнес-логика
    │   ├── repositories.py     # Репозитории
    │   ├── subscribers.py      # RabbitMQ подписчики
    │   ├── routes.py           # API маршруты
    │   ├── dependencies.py
    │   ├── enums.py
    │   ├── exceptions.py
    │   └── __init__.py
    └── outbox/                 # Outbox pattern
        ├── models.py           # ORM модели
        ├── schemas.py          # Pydantic схемы
        ├── services.py         # Сервис outbox
        ├── repositories.py     # Репозитории
        ├── tasks.py            # Задачи
        ├── dependencies.py
        ├── enums.py
        └── __init__.py
```

## API

### Платежи

#### Создание платежа

```
POST /api/v1/payments
Headers:
  Idempotency-Key: <uuid>
  X-API-Key: <api-key>
Body:
{
  "amount": 100.00,
  "currency": "RUB",
  "description": "Payment description",
  "metadata": {},
  "webhook_url": "https://example.com/webhook"
}
Response: 202 Accepted
```

#### Получение платежа

```
GET /api/v1/payments/{payment_id}
Headers:
  X-API-Key: <api-key>
Response: 200 OK
```

### RabbitMQ очереди

| Очередь | Назначение |
|---|---|
| `payment.new` | Новые платежи для обработки |
| `payment.dlq` | Dead Letter Queue для неудачных обработок |

## Зависимости

### Основные

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **asyncpg** — асинхронный драйвер PostgreSQL
- **FastStream** — работа с RabbitMQ
- **Alembic** — миграции базы данных
- **Pydantic Settings** — конфигурация
- **Tenacity** — retry-логика

### Dev

- **pytest** + **pytest-asyncio** + **pytest-mock** — тестирование
- **ruff** — линтер и форматирование

## Docker

### Dockerfile

Dockerfile находится в [`app/Dockerfile`](app/Dockerfile).

### Docker Compose

Файлы для локальной разработки:

| Файл | Назначение |
|---|---|
| `.build/local/compose.yaml` | Основной compose файл |
| `.build/local/compose.override.yaml` | Override для разработки |
| `.build/local/.env.example` | Шаблон переменных окружения |
| `.build/local/app/Dockerfile` | Dockerfile для приложения |

### Сборка и запуск

```bash
cd .build/local

# Сборка образов
docker compose build

# Запуск
docker compose up -d

# Остановка
docker compose stop

# Очистка (с удалением данных)
docker compose down -v
```
