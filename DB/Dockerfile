# Builder stage
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_PYTHON_DOWNLOADS=1

WORKDIR /app

ADD pyproject.toml /app/pyproject.toml
ADD packages /app/packages
ADD services/a_service services/a_service

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-packages --no-install-project --no-dev

# Runtime stage
FROM python:3.11-slim

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app:/app/services/a_service

USER app
WORKDIR /app/services/a_service

EXPOSE 8000 50051
CMD ["uvicorn", "app.main:app", "--workers 2"]