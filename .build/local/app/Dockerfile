FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
ENV UV_INSTALL_DIR=/usr/local/bin
RUN chmod +x /uv-installer.sh \
    && sh /uv-installer.sh \
    && rm /uv-installer.sh

RUN groupadd --system app \
    && useradd --system --gid app --no-create-home --home-dir /app app \
    && mkdir -p /app /opt/uv-cache /opt/venv \
    && chown -R app:app /app /opt/uv-cache /opt/venv

USER app

ENV HOME=/app \
    UV_CACHE_DIR=/opt/uv-cache \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --chown=app:app ../app/uv.lock ../app/pyproject.toml /app/
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app:app . /app
RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD curl -f http://localhost:8000/api/v1/healthz || exit 1

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
