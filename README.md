# payment-processing-service

Сервис для обработки платежей. Построен на FastAPI с использованием асинхронной базы данных PostgreSQL и брокера сообщений RabbitMQ.

## Базовая конфигурация

Проект использует файловую конфигурацию через `.env` (или другие файлы окружения, поддерживаемые `pydantic-settings`). Конфигурация находится в [`app/src/core/config.py`](app/src/core/config.py).

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
| `DB_HOST` | Адрес сервера PostgreSQL | — |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_USER` | Имя пользователя | — |
| `DB_PASSWORD` | Пароль | — |
| `DB_DATABASE` | Имя базы данных | — |
| `DB_POOL_SIZE` | Размер пула соединений | `5` |
| `DB_POOL_MAX_OVERFLOW` | Максимум переполнений пула | `10` |
| `DB_POOL_TIMEOUT` | Таймаут получения соединения (сек) | `30` |
| `DB_POOL_RECYCLE` | Время жизни соединения (сек) | `3600` |

#### CORS и доверенные хосты

| Переменная | Описание | По умолчанию |
|---|---|---|
| `CORS_ALLOW_ORIGINS` | Список разрешённых origins (через запятую) | `[]` |
| `CORS_ALLOW_CREDENTIALS` | Разрешить cookies | `False` |
| `CORS_ALLOW_METHODS` | Разрешённые HTTP методы | `GET,POST,PATCH,DELETE,OPTIONS` |
| `CORS_ALLOW_HEADERS` | Разрешённые заголовки | `Authorization,Content-Type` |
| `TRUSTED_HOSTS` | Доверенные хосты (через запятую) | `[]` |

> **Примечание:** При `ENVIRONMENT=local` настройки CORS автоматически расширяются до `*`, а `TRUSTED_HOSTS` устанавливается в `*`.

## Локальный запуск

### Требования

- Python >= 3.12, < 3.13
- PostgreSQL (локально или в Docker)
- RabbitMQ (локально или в Docker)

### Установка

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

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=payment_processing

CORS_ALLOW_ORIGINS=*
TRUSTED_HOSTS=*
```

### Запуск

#### С помощью uvicorn:

```bash
cd app
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### С помощью fastapi dev:

```bash
cd app
uv run fastapi dev src/main.py
```

API будет доступен по адресу: `http://localhost:8000/api/v1`

- Swagger UI (документация): `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Миграции базы данных (Alembic)

```bash
cd app

# Инициализация (первый раз)
uv run alembic init migrations

# Создание новой миграции
uv run alembic revision --autogenerate -m "description"

# Применение миграций
uv run alembic upgrade head

# Откат последней миграции
uv run alembic downgrade -1
```

### Запуск зависимостей в Docker

```bash
# PostgreSQL
docker run --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=payment_processing \
  -p 5432:5432 \
  -d postgres:16

# RabbitMQ (с управлением через Web UI)
docker run --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -d rabbitmq:3-management
```

RabbitMQ Web UI доступен по адресу: [`http://localhost:15672`](http://localhost:15672)

**Данные для входа по умолчанию:**
- **Логин:** `guest`
- **Пароль:** `guest`

> **Примечание:** Web UI доступен только при использовании образа с тегом `management` (например, `rabbitmq:3-management`). По умолчанию RabbitMQ слушает порт 5672 для протокола AMQP, а порт 15672 — для Web UI.

## Структура проекта

```
app/
├── pyproject.toml          # Зависимости и конфигурация
├── alembic.ini             # Конфигурация Alembic
├── migrations/             # Миграции базы данных
│   ├── env.py
│   └── versions/
└── src/
    ├── __init__.py
    ├── main.py             # Точка входа (FastAPI приложение)
    └── core/
        ├── config.py       # Настройки и конфигурация
        ├── enums.py        # Перечисления
        ├── events.py       # События жизненного цикла
        ├── exceptions.py   # Исключения
        ├── exception_handlers.py  # Обработчики ошибок
        ├── logging.py      # Настройка логирования
        ├── middleware.py   # Middleware
        ├── responses.py    # Форматы ответов
        ├── routes.py       # Маршрутизация
        ├── broker/         # Конфигурация RabbitMQ
        └── db/             # Конфигурация базы данных
```

## Зависимости

### Основные

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **asyncpg** — асинхронный драйвер PostgreSQL
- **FastStream** — работа с RabbitMQ
- **Alembic** — миграции базы данных
- **Pydantic Settings** — конфигурация

### Dev

- **pytest** + **pytest-asyncio** + **pytest-mock** — тестирование
- **ruff** — линтер и форматирование
