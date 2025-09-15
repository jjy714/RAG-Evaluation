# Stage 1: Use an official Python runtime with uv pre-installed
# This image is equivalent to python:3.12-slim but includes uv

FROM python3.12-bookworm-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


WORKDIR /app

# Copy the project into the image
COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

LABEL version="1.0" maintainer="Jason Jung <jason@example.com>"



RUN uv sync --locked

EXPOSE 8000

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "uvicorn", "main:app", "--port", "8000"]