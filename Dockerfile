# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 libpq-dev && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_DEV=1

WORKDIR /app

# Install uv binary (pinned)
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

# Prime deps layer from lockfiles
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable

# Add source and install project (non-editable, byte-compiled)
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 libpq-dev && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Non-root runtime
RUN useradd --create-home app
USER app

# Bring in the prebuilt environment only
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Default entrypoint (console script from pyproject)
CMD ["marketplace"]
