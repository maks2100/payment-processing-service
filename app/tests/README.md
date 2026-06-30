# Test Infrastructure

## Overview

This directory contains the test infrastructure for the payment-processing-service.
Tests use pytest with pytest-asyncio for async test support and pytest-mock for mocking.

## Structure

```
tests/
├── __init__.py      # Makes tests a Python package
├── conftest.py      # Root-level pytest configuration
└── README.md        # This file
```

## Configuration

The pytest configuration is defined in [`pyproject.toml`](../pyproject.toml) under `[tool.pytest.ini_options]`:

| Setting | Value | Purpose |
|---------|-------|---------|
| `testpaths` | `["tests"]` | Specifies the test directory |
| `pythonpath` | `["src"]` | Allows importing from `src` directly in tests |
| `asyncio_mode` | `"auto"` | Auto-detects async tests via pytest-asyncio |
| `markers` | `slow, integration, unit` | Custom markers for test categorization |

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run only unit tests
uv run pytest -m unit

# Exclude slow tests
uv run pytest -m "not slow"

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific file
uv run pytest tests/test_example.py

# Run with detailed report
uv run pytest --tb=long -v
```

## Writing Tests

### Importing from the application

Thanks to `pythonpath = ["src"]` in pytest config, you can import directly:

```python
from src.core.config import Settings
from src.core.db.manager import async_db_manager
```

### Async tests

With `asyncio_mode = "auto"`, async test functions work without decorators:

```python
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### Using pytest-mock

```python
from unittest.mock import MagicMock

async def test_with_mock(mock: MagicMock):
    mock.return_value = "test"
    # ...
```

### Using httpx for FastAPI testing

```python
from httpx import AsyncClient
from src.main import create_application

async def test_endpoint():
    app = create_application()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/healthz")
        assert response.status_code == 200
```

## Dependencies

- `pytest>=9.1.1`
- `pytest-asyncio>=1.4.0`
- `pytest-mock>=3.15.1`
- `httpx` (for FastAPI testing)

## Best Practices

1. **Use markers** to categorize tests: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
2. **Keep tests isolated** — each test should be independent
3. **Use fixtures** for shared test setup (create in `conftest.py` or test file)
4. **Mock external dependencies** (DB, RabbitMQ, HTTP clients)
5. **Name test files** with `test_` prefix (e.g., `test_config.py`)
6. **Name test functions** with `test_` prefix (e.g., `test_settings_validation`)
